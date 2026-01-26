using System;
using System.Collections.Generic;
using System.Net.WebSockets;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading;
using System.Threading.Tasks;
using OCPPSimulator.Models;

namespace OCPPSimulator.Clients;

/// <summary>
/// OCPP 2.0.1 클라이언트 - 표준 .NET WebSocket 사용
/// </summary>
public class OCPPClient : IDisposable
{
    private WebSocket? _websocket;
    private readonly string _chargerId;
    private readonly string _serverUrl;
    private readonly double _maxPower;
    private CancellationTokenSource? _cancellationTokenSource;
    private Task? _receiveTask;

    // 충전기 상태
    public ChargerStatus CurrentStatus { get; set; } = ChargerStatus.Available;
    public double EnergyAccumulated { get; set; } = 0.0;
    public double CurrentPower { get; set; } = 0.0;
    public string? TransactionId { get; set; } = null;
    public bool IsConnected { get; private set; } = false;
    public bool IsCharging { get; set; } = false;

    // JSON 직렬화 옵션
    private readonly JsonSerializerOptions _jsonOptions = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
        WriteIndented = false
    };

    public OCPPClient(string chargerId, string serverUrl = "ws://127.0.0.1:9000", double maxPower = 100)
    {
        _chargerId = chargerId;
        _serverUrl = serverUrl;
        _maxPower = maxPower;
    }

    /// <summary>
    /// 서버에 연결
    /// </summary>
    public async Task ConnectAsync()
    {
        try
        {
            string chargerUrl = $"{_serverUrl}/{_chargerId}";
            Console.WriteLine($"[{_chargerId}] 서버에 연결 중... ({chargerUrl})");

            // ClientWebSocket을 동적으로 생성 (System.Net.WebSockets.Client NuGet 패키지가 설치된 경우)
            var clientWSType = Type.GetType("System.Net.WebSockets.Client.ClientWebSocket, System.Net.WebSockets.Client");
            if (clientWSType == null)
            {
                throw new InvalidOperationException("ClientWebSocket을 찾을 수 없습니다. System.Net.WebSockets.Client 패키지가 필요합니다.");
            }

            // 인스턴스 생성
            _websocket = (WebSocket?)Activator.CreateInstance(clientWSType);
            if (_websocket == null)
            {
                throw new InvalidOperationException("ClientWebSocket 인스턴스를 생성할 수 없습니다.");
            }

            // Options 속성에서 AddSubprotocol 메서드 호출
            var optionsProperty = clientWSType.GetProperty("Options");
            if (optionsProperty != null)
            {
                var options = optionsProperty.GetValue(_websocket);
                if (options != null)
                {
                    var method = options.GetType().GetMethod("AddSubprotocol");
                    method?.Invoke(options, new object[] { "ocpp2.0.1" });
                }
            }

            var uri = new Uri(chargerUrl);
            var cts = new CancellationTokenSource(TimeSpan.FromSeconds(10));

            // ConnectAsync를 동적으로 호출
            var connectMethod = clientWSType.GetMethod("ConnectAsync", 
                new[] { typeof(Uri), typeof(CancellationToken) });
            if (connectMethod == null)
            {
                throw new InvalidOperationException("ConnectAsync 메서드를 찾을 수 없습니다.");
            }

            var connectTask = (Task?)connectMethod.Invoke(_websocket, new object[] { uri, cts.Token });
            if (connectTask == null)
            {
                throw new InvalidOperationException("ConnectAsync 호출에 실패했습니다.");
            }

            await connectTask;

            IsConnected = true;
            Console.WriteLine($"[{_chargerId}] WebSocket 연결 성공");

            // BootNotification 전송
            await SendBootNotificationAsync();

            // 메시지 수신 태스크 시작
            _cancellationTokenSource = new CancellationTokenSource();
            _receiveTask = ReceiveMessagesAsync(_cancellationTokenSource.Token);

            // Heartbeat 태스크 시작
            _ = SendHeartbeatLoopAsync(_cancellationTokenSource.Token);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[{_chargerId}] 연결 오류: {ex.Message}");
            IsConnected = false;
        }
    }

    /// <summary>
    /// WebSocket 메시지 수신
    /// </summary>
    private async Task ReceiveMessagesAsync(CancellationToken cancellationToken)
    {
        try
        {
            byte[] buffer = new byte[4096];

            while (IsConnected && !cancellationToken.IsCancellationRequested)
            {
                if (_websocket == null)
                    break;

                var result = await _websocket.ReceiveAsync(
                    new ArraySegment<byte>(buffer),
                    cancellationToken
                );

                if (result.MessageType == WebSocketMessageType.Close)
                {
                    await _websocket.CloseAsync(
                        WebSocketCloseStatus.NormalClosure,
                        "Closing",
                        CancellationToken.None
                    );
                    IsConnected = false;
                    break;
                }

                if (result.MessageType == WebSocketMessageType.Text)
                {
                    string message = Encoding.UTF8.GetString(buffer, 0, result.Count);
                    Console.WriteLine($"[{_chargerId}] 메시지 수신: {message[..Math.Min(80, message.Length)]}...");

                    try
                    {
                        var array = JsonSerializer.Deserialize<JsonElement[]>(message);
                        if (array != null && array.Length >= 2)
                        {
                            int msgType = array[0].GetInt32();

                            if (msgType == (int)MessageType.CALLRESULT)
                            {
                                string msgId = array[1].GetString() ?? "unknown";
                                Console.WriteLine($"[{_chargerId}] CALLRESULT 수신: {msgId}");
                            }
                            else if (msgType == (int)MessageType.CALL && array.Length >= 3)
                            {
                                string action = array[2].GetString() ?? "Unknown";
                                var payload = array.Length > 3 ? array[3] : new JsonElement();
                                HandleCall(action, array[1].GetString() ?? "", payload);
                            }
                        }
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"[{_chargerId}] 메시지 처리 오류: {ex.Message}");
                    }
                }
            }
        }
        catch (OperationCanceledException)
        {
            // 예상된 취소
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[{_chargerId}] 메시지 수신 오류: {ex.Message}");
            IsConnected = false;
        }
    }

    /// <summary>
    /// CALL 메시지 처리
    /// </summary>
    private void HandleCall(string action, string msgId, JsonElement payload)
    {
        Console.WriteLine($"[{_chargerId}] CALL 수신: {action}");

        switch (action)
        {
            case "RequestStartTransaction":
                HandleRequestStartTransaction(msgId, payload);
                break;

            case "RequestStopTransaction":
                HandleRequestStopTransaction(msgId, payload);
                break;

            case "SetChargingProfile":
                HandleSetChargingProfile(msgId, payload);
                break;

            default:
                SendCallResult(msgId, new { status = "Accepted" });
                break;
        }
    }

    /// <summary>
    /// 충전 시작 요청 처리
    /// </summary>
    private void HandleRequestStartTransaction(string msgId, JsonElement payload)
    {
        try
        {
            string idToken = "unknown";
            if (payload.TryGetProperty("idToken", out var idTokenElement) &&
                idTokenElement.TryGetProperty("idToken", out var token))
            {
                idToken = token.GetString() ?? "unknown";
            }

            Console.WriteLine($"[{_chargerId}] 충전 시작 요청: {idToken}");
            SendCallResult(msgId, new { status = "Accepted" });

            // 충전 시작
            _ = StartChargingAsync(idToken);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[{_chargerId}] 충전 시작 오류: {ex.Message}");
            SendCallResult(msgId, new { status = "Rejected" });
        }
    }

    /// <summary>
    /// 충전 중지 요청 처리
    /// </summary>
    private void HandleRequestStopTransaction(string msgId, JsonElement payload)
    {
        try
        {
            Console.WriteLine($"[{_chargerId}] 충전 중지 요청");
            SendCallResult(msgId, new { status = "Accepted" });

            // 충전 중지
            _ = StopChargingAsync();
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[{_chargerId}] 충전 중지 오류: {ex.Message}");
            SendCallResult(msgId, new { status = "Rejected" });
        }
    }

    /// <summary>
    /// 충전 프로필 설정 처리
    /// </summary>
    private void HandleSetChargingProfile(string msgId, JsonElement payload)
    {
        try
        {
            if (payload.TryGetProperty("chargingProfile", out var profileElement) &&
                profileElement.TryGetProperty("chargingSchedule", out var scheduleElement) &&
                scheduleElement.TryGetProperty("chargingSchedulePeriod", out var periodElement) &&
                periodElement.ValueKind == JsonValueKind.Array &&
                periodElement.GetArrayLength() > 0)
            {
                var firstPeriod = periodElement[0];
                if (firstPeriod.TryGetProperty("limit", out var limitElement))
                {
                    double limit = limitElement.GetDouble() / 1000;
                    CurrentPower = Math.Min(limit, _maxPower);
                    Console.WriteLine($"[{_chargerId}] 충전 프로필 설정: {CurrentPower}kW");
                }
            }

            SendCallResult(msgId, new { status = "Accepted" });
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[{_chargerId}] 충전 프로필 설정 오류: {ex.Message}");
            SendCallResult(msgId, new { status = "Rejected" });
        }
    }

    /// <summary>
    /// BootNotification 전송
    /// </summary>
    private async Task SendBootNotificationAsync()
    {
        try
        {
            string msgId = Guid.NewGuid().ToString()[..12];
            var request = new BootNotificationRequest
            {
                ChargingStation = new ChargingStationInfo
                {
                    Model = "CSharpSimulator",
                    VendorName = "OCPP.NET",
                    SerialNumber = $"SN-{_chargerId}-001",
                    FirmwareVersion = "1.0.0"
                },
                Reason = "PowerUp"
            };

            var payload = JsonSerializer.Serialize(request, _jsonOptions);
            var message = new object[] { (int)MessageType.CALL, msgId, "BootNotification", JsonSerializer.Deserialize<JsonElement>(payload) };

            string json = JsonSerializer.Serialize(message, _jsonOptions);
            await SendRawAsync(json);

            Console.WriteLine($"[{_chargerId}] BootNotification 전송");
            CurrentStatus = ChargerStatus.Available;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[{_chargerId}] BootNotification 전송 오류: {ex.Message}");
        }
    }

    /// <summary>
    /// Heartbeat 루프 (30초마다)
    /// </summary>
    private async Task SendHeartbeatLoopAsync(CancellationToken cancellationToken)
    {
        try
        {
            while (!cancellationToken.IsCancellationRequested && IsConnected)
            {
                await Task.Delay(30000, cancellationToken);

                if (!IsConnected)
                    break;

                string msgId = Guid.NewGuid().ToString()[..12];
                var request = new HeartbeatRequest { CurrentTime = DateTime.UtcNow.ToString("O") + "Z" };
                var payload = JsonSerializer.Serialize(request, _jsonOptions);
                var message = new object[] { (int)MessageType.CALL, msgId, "Heartbeat", JsonSerializer.Deserialize<JsonElement>(payload) };

                string json = JsonSerializer.Serialize(message, _jsonOptions);
                await SendRawAsync(json);

                Console.WriteLine($"[{_chargerId}] Heartbeat 전송");
            }
        }
        catch (OperationCanceledException)
        {
            // 예상된 취소
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[{_chargerId}] Heartbeat 오류: {ex.Message}");
        }
    }

    /// <summary>
    /// 충전 시작
    /// </summary>
    public async Task StartChargingAsync(string idToken = "user_token")
    {
        try
        {
            if (CurrentStatus != ChargerStatus.Available)
            {
                Console.WriteLine($"[{_chargerId}] 이미 충전 중 또는 준비 중");
                return;
            }

            CurrentStatus = ChargerStatus.Preparing;
            TransactionId = Guid.NewGuid().ToString()[..8];
            EnergyAccumulated = 0.0;
            IsCharging = true;

            // TransactionEvent - Started
            await SendTransactionEventAsync("Started", idToken);

            await Task.Delay(2000);
            CurrentStatus = ChargerStatus.Charging;
            CurrentPower = _maxPower;

            // TransactionEvent - Updated
            await SendTransactionEventAsync("Updated", idToken);

            Console.WriteLine($"[{_chargerId}] 충전 시작: {TransactionId}");

            // 충전 시뮬레이션
            _ = SimulateChargingAsync();
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[{_chargerId}] 충전 시작 오류: {ex.Message}");
        }
    }

    /// <summary>
    /// 충전 중지
    /// </summary>
    public async Task StopChargingAsync()
    {
        try
        {
            if (!IsCharging)
            {
                Console.WriteLine($"[{_chargerId}] 현재 충전 중이 아님");
                return;
            }

            IsCharging = false;
            CurrentStatus = ChargerStatus.Finishing;

            // TransactionEvent - Updated
            await SendTransactionEventAsync("Updated", "user_token");

            await Task.Delay(1000);

            // TransactionEvent - Ended
            await SendTransactionEventAsync("Ended", "user_token");

            CurrentStatus = ChargerStatus.Available;
            CurrentPower = 0.0;

            Console.WriteLine($"[{_chargerId}] 충전 완료: {TransactionId} (누적: {EnergyAccumulated:F2} kWh)");

            TransactionId = null;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[{_chargerId}] 충전 중지 오류: {ex.Message}");
        }
    }

    /// <summary>
    /// 충전 시뮬레이션 (에너지 누적)
    /// </summary>
    private async Task SimulateChargingAsync()
    {
        try
        {
            while (IsCharging)
            {
                await Task.Delay(5000); // 5초마다

                if (!IsCharging)
                    break;

                // 에너지 누적 (전력 * 시간)
                double energyPerSecond = CurrentPower / 3600;
                EnergyAccumulated += energyPerSecond * 5;

                // 80% 이후 전력 감소
                if (EnergyAccumulated > 20)
                {
                    CurrentPower = _maxPower * 0.7;
                }

                // TransactionEvent - Updated
                await SendTransactionEventAsync("Updated", "user_token");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[{_chargerId}] 충전 시뮬레이션 오류: {ex.Message}");
        }
    }

    /// <summary>
    /// TransactionEvent 전송
    /// </summary>
    public async Task SendTransactionEventAsync(string eventType, string idToken)
    {
        try
        {
            string msgId = Guid.NewGuid().ToString()[..12];

            var transactionData = new TransactionData
            {
                TransactionId = TransactionId ?? "unknown",
                ChargingState = CurrentStatus.ToString(),
                TimeSpentCharging = 0,
                StoppedReason = eventType == "Ended" ? "Local" : null,
                TotalCost = (decimal)(EnergyAccumulated * 150),
                ChargingPeriods = new List<ChargingPeriod>
                {
                    new ChargingPeriod
                    {
                        StartDateTime = DateTime.UtcNow.ToString("O") + "Z",
                        Dimensions = new List<Dimension>
                        {
                            new Dimension
                            {
                                Name = "Energy.Active.Import.Register",
                                Unit = "Wh",
                                UnitMultiplier = 1,
                                Value = (decimal)(EnergyAccumulated * 1000)
                            },
                            new Dimension
                            {
                                Name = "Power.Active.Import",
                                Unit = "W",
                                UnitMultiplier = 1000,
                                Value = (decimal)CurrentPower
                            }
                        }
                    }
                }
            };

            var request = new TransactionEventRequest
            {
                EventType = eventType,
                Timestamp = DateTime.UtcNow.ToString("O") + "Z",
                TriggerReason = "Authorized",
                SeqNo = 0,
                TransactionData = transactionData
            };

            var payload = JsonSerializer.Serialize(request, _jsonOptions);
            var message = new object[] { (int)MessageType.CALL, msgId, "TransactionEvent", JsonSerializer.Deserialize<JsonElement>(payload) };

            string json = JsonSerializer.Serialize(message, _jsonOptions);
            await SendRawAsync(json);

            Console.WriteLine($"[{_chargerId}] TransactionEvent 전송 ({eventType}): {EnergyAccumulated:F2} kWh");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[{_chargerId}] TransactionEvent 전송 오류: {ex.Message}");
        }
    }

    /// <summary>
    /// CALLRESULT 전송
    /// </summary>
    private void SendCallResult(string msgId, object payload)
    {
        try
        {
            var payloadJson = JsonSerializer.Serialize(payload, _jsonOptions);
            var message = new object[] { (int)MessageType.CALLRESULT, msgId, JsonSerializer.Deserialize<JsonElement>(payloadJson) };

            string json = JsonSerializer.Serialize(message, _jsonOptions);
            _ = SendRawAsync(json);

            Console.WriteLine($"[{_chargerId}] CALLRESULT 전송: {msgId}");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[{_chargerId}] CALLRESULT 전송 오류: {ex.Message}");
        }
    }

    /// <summary>
    /// StatusNotification 전송
    /// </summary>
    public async Task SendStatusNotificationAsync()
    {
        try
        {
            string msgId = Guid.NewGuid().ToString()[..12];
            var request = new StatusNotificationRequest
            {
                Timestamp = DateTime.UtcNow.ToString("O") + "Z",
                ConnectorStatus = CurrentStatus.ToString(),
                EvseId = 1,
                ConnectorId = 1
            };

            var payload = JsonSerializer.Serialize(request, _jsonOptions);
            var message = new object[] { (int)MessageType.CALL, msgId, "StatusNotification", JsonSerializer.Deserialize<JsonElement>(payload) };

            string json = JsonSerializer.Serialize(message, _jsonOptions);
            await SendRawAsync(json);

            Console.WriteLine($"[{_chargerId}] StatusNotification 전송: {CurrentStatus}");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[{_chargerId}] StatusNotification 전송 오류: {ex.Message}");
        }
    }

    /// <summary>
    /// 원본 JSON 문자열 전송
    /// </summary>
    private async Task SendRawAsync(string message)
    {
        try
        {
            if (_websocket == null || _websocket.State != WebSocketState.Open)
                return;

            byte[] buffer = Encoding.UTF8.GetBytes(message);
            await _websocket.SendAsync(
                new ArraySegment<byte>(buffer),
                WebSocketMessageType.Text,
                true,
                CancellationToken.None
            );
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[{_chargerId}] 메시지 전송 오류: {ex.Message}");
        }
    }

    /// <summary>
    /// 연결 해제
    /// </summary>
    public async Task DisconnectAsync()
    {
        try
        {
            IsConnected = false;
            _cancellationTokenSource?.Cancel();

            if (_websocket?.State == WebSocketState.Open)
            {
                await _websocket.CloseAsync(
                    WebSocketCloseStatus.NormalClosure,
                    "Closing",
                    CancellationToken.None
                );
            }

            Console.WriteLine($"[{_chargerId}] 연결 해제");

            await Task.Delay(100);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[{_chargerId}] 연결 해제 오류: {ex.Message}");
        }
    }

    /// <summary>
    /// 현재 상태 조회
    /// </summary>
    public string GetStatus()
    {
        return $"[{_chargerId}] 상태: {CurrentStatus}, 전력: {CurrentPower}kW, 누적: {EnergyAccumulated:F2}kWh";
    }

    /// <summary>
    /// 리소스 정리
    /// </summary>
    public void Dispose()
    {
        _websocket?.Dispose();
        _cancellationTokenSource?.Dispose();
    }
}
