using System;
using System.Collections.Generic;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading;
using System.Threading.Tasks;
using WebSocketSharp;

namespace OCPP201ChargerSimulator
{
    /// <summary>
    /// OCPP 2.0.1 메시지 기본 구조
    /// </summary>
    public class OCPPMessage
    {
        [JsonPropertyName("messageTypeId")]
        public int MessageTypeId { get; set; }

        [JsonPropertyName("messageId")]
        public string MessageId { get; set; }

        [JsonPropertyName("action")]
        public string Action { get; set; }

        [JsonPropertyName("payload")]
        public JsonElement Payload { get; set; }

        [JsonPropertyName("errorCode")]
        public string ErrorCode { get; set; }

        [JsonPropertyName("errorDescription")]
        public string ErrorDescription { get; set; }
    }

    /// <summary>
    /// 충전기 상태 열거형
    /// </summary>
    public enum ChargerStatus
    {
        Available,
        Preparing,
        Charging,
        SuspendedEVSE,
        SuspendedEV,
        Finishing,
        Reserved,
        Unavailable,
        Faulted
    }

    /// <summary>
    /// OCPP 2.0.1 충전기 시뮬레이터
    /// </summary>
    public class ChargerSimulator
    {
        // 기본 설정
        public string ChargerId { get; set; }
        public string ServerUrl { get; set; }
        public string ChargerModel { get; set; }
        public string Vendor { get; set; }

        // 상태 정보
        private ChargerStatus _currentStatus;
        private double _currentPower = 0;
        private double _energyAccumulated = 0;
        private string _currentTransactionId;
        private WebSocket _webSocket;

        // 설정값
        private double _maxPower = 100; // kW
        private int _heartbeatInterval = 30; // 초
        private bool _isConnected = false;
        private bool _isBootNotificationSent = false;

        // 이벤트
        public event EventHandler<string> OnMessageSent;
        public event EventHandler<string> OnMessageReceived;
        public event EventHandler<Exception> OnError;

        public ChargerSimulator(
            string chargerId,
            string serverUrl = "ws://localhost:9000",
            string chargerModel = "EVBox Home",
            string vendor = "EVBox")
        {
            ChargerId = chargerId;
            ServerUrl = serverUrl;
            ChargerModel = chargerModel;
            Vendor = vendor;
            _currentStatus = ChargerStatus.Available;
        }

        /// <summary>
        /// 서버에 연결
        /// </summary>
        public async Task ConnectAsync()
        {
            try
            {
                Console.WriteLine($"[{ChargerId}] 서버 연결 중... ({ServerUrl})");

                _webSocket = new WebSocket(ServerUrl);
                _webSocket.OnMessage += OnWebSocketMessage;
                _webSocket.OnError += OnWebSocketError;
                _webSocket.OnClose += OnWebSocketClose;

                _webSocket.Connect();
                _isConnected = _webSocket.IsAlive;

                if (_isConnected)
                {
                    Console.WriteLine($"✅ [{ChargerId}] 서버 연결 성공");
                    await Task.Delay(500);
                    await SendBootNotificationAsync();
                    StartHeartbeat();
                }
                else
                {
                    throw new Exception("WebSocket 연결 실패");
                }
            }
            catch (Exception ex)
            {
                OnError?.Invoke(this, ex);
                Console.WriteLine($"❌ [{ChargerId}] 연결 오류: {ex.Message}");
            }
        }

        /// <summary>
        /// BootNotification 메시지 전송
        /// </summary>
        private async Task SendBootNotificationAsync()
        {
            try
            {
                var messageId = Guid.NewGuid().ToString("N").Substring(0, 12);
                
                var payload = new
                {
                    chargingStation = new
                    {
                        model = ChargerModel,
                        vendorName = Vendor,
                        serialNumber = $"SN-{ChargerId}-001",
                        firmwareVersion = "1.0.0"
                    },
                    reason = "PowerUp"
                };

                var message = JsonSerializer.Serialize(new object[]
                {
                    2, // CALL 메시지 타입
                    messageId,
                    "BootNotification",
                    payload
                });

                SendMessage(message);
                _isBootNotificationSent = true;
                _currentStatus = ChargerStatus.Available;

                Console.WriteLine($"📤 [{ChargerId}] BootNotification 전송");
                await Task.Delay(1000);
            }
            catch (Exception ex)
            {
                OnError?.Invoke(this, ex);
            }
        }

        /// <summary>
        /// 하트비트 시작
        /// </summary>
        private void StartHeartbeat()
        {
            var heartbeatTask = Task.Run(async () =>
            {
                while (_isConnected && _isBootNotificationSent)
                {
                    await Task.Delay(_heartbeatInterval * 1000);
                    await SendHeartbeatAsync();
                }
            });
        }

        /// <summary>
        /// Heartbeat 메시지 전송
        /// </summary>
        private async Task SendHeartbeatAsync()
        {
            try
            {
                var messageId = Guid.NewGuid().ToString("N").Substring(0, 12);
                var currentTime = DateTime.UtcNow.ToString("o");

                var message = JsonSerializer.Serialize(new object[]
                {
                    2, // CALL 메시지 타입
                    messageId,
                    "Heartbeat",
                    new { currentTime }
                });

                SendMessage(message);
                Console.WriteLine($"💓 [{ChargerId}] Heartbeat 전송 ({DateTime.Now:HH:mm:ss})");
            }
            catch (Exception ex)
            {
                OnError?.Invoke(this, ex);
            }
        }

        /// <summary>
        /// 충전 시작 (서버 요청 대기 또는 자동 시작)
        /// </summary>
        public async Task StartChargingAsync(string idToken)
        {
            try
            {
                if (_currentStatus != ChargerStatus.Available)
                {
                    Console.WriteLine($"⚠️ [{ChargerId}] 현재 상태에서는 충전을 시작할 수 없음: {_currentStatus}");
                    return;
                }

                _currentStatus = ChargerStatus.Preparing;
                _currentTransactionId = Guid.NewGuid().ToString("N").Substring(0, 8);
                _energyAccumulated = 0;
                _currentPower = 0;

                // TransactionEvent - Started
                await SendTransactionEventAsync("Started", idToken);

                // 준비 상태에서 충전 상태로 전환
                await Task.Delay(2000);
                _currentStatus = ChargerStatus.Charging;
                _currentPower = _maxPower;

                // TransactionEvent - Updated
                await SendTransactionEventAsync("Updated", idToken);

                Console.WriteLine($"🔌 [{ChargerId}] 충전 시작: {_currentTransactionId}");
                
                // 충전 시뮬레이션 시작
                StartChargingSimulation();
            }
            catch (Exception ex)
            {
                OnError?.Invoke(this, ex);
            }
        }

        /// <summary>
        /// 충전 시뮬레이션 (전력 소비)
        /// </summary>
        private void StartChargingSimulation()
        {
            var chargingTask = Task.Run(async () =>
            {
                while (_isConnected && _currentStatus == ChargerStatus.Charging)
                {
                    // 실제 충전 상황을 시뮬레이션 (초당 약간의 에너지 증가)
                    double energyPerSecond = (_currentPower / 3600); // kWh로 변환
                    _energyAccumulated += energyPerSecond;

                    // 80% 충전 시 충전 속도 감소 (배터리 곡선 시뮬레이션)
                    if (_energyAccumulated > 20) // 25kWh * 80% 가정
                    {
                        _currentPower = _maxPower * 0.7;
                    }

                    await Task.Delay(5000); // 5초마다 업데이트

                    if (_currentStatus == ChargerStatus.Charging)
                    {
                        await SendTransactionEventAsync("Updated", "user_token");
                    }
                }
            });
        }

        /// <summary>
        /// 충전 중지
        /// </summary>
        public async Task StopChargingAsync()
        {
            try
            {
                if (_currentStatus != ChargerStatus.Charging && 
                    _currentStatus != ChargerStatus.Preparing &&
                    _currentStatus != ChargerStatus.SuspendedEVSE &&
                    _currentStatus != ChargerStatus.SuspendedEV)
                {
                    Console.WriteLine($"⚠️ [{ChargerId}] 현재 상태에서는 충전을 중지할 수 없음: {_currentStatus}");
                    return;
                }

                _currentStatus = ChargerStatus.Finishing;
                await SendTransactionEventAsync("Updated", "user_token");

                await Task.Delay(1000);

                // TransactionEvent - Ended
                await SendTransactionEventAsync("Ended", "user_token");

                _currentStatus = ChargerStatus.Available;
                _currentPower = 0;

                Console.WriteLine($"⏹️ [{ChargerId}] 충전 중지: {_currentTransactionId} (누적: {_energyAccumulated:F2} kWh)");
                _currentTransactionId = null;
            }
            catch (Exception ex)
            {
                OnError?.Invoke(this, ex);
            }
        }

        /// <summary>
        /// TransactionEvent 전송
        /// </summary>
        private async Task SendTransactionEventAsync(string eventType, string idToken)
        {
            try
            {
                var messageId = Guid.NewGuid().ToString("N").Substring(0, 12);
                var currentTime = DateTime.UtcNow.ToString("o");

                var payload = new
                {
                    eventType,
                    timestamp = currentTime,
                    triggerReason = "Authorized",
                    seqNo = 0,
                    transactionData = new
                    {
                        transactionId = _currentTransactionId,
                        chargingState = _currentStatus.ToString(),
                        timeSpentCharging = 0,
                        stoppedReason = eventType == "Ended" ? "Local" : null,
                        totalCost = Math.Round(_energyAccumulated * 150, 2), // ₩150/kWh 가정
                        chargingPeriods = new[]
                        {
                            new
                            {
                                startDateTime = DateTime.UtcNow.AddSeconds(-60).ToString("o"),
                                dimensions = new[]
                                {
                                    new
                                    {
                                        name = "Energy.Active.Import.Register",
                                        unit = "Wh",
                                        unitMultiplier = 1,
                                        value = _energyAccumulated * 1000 // Wh로 변환
                                    },
                                    new
                                    {
                                        name = "Power.Active.Import",
                                        unit = "W",
                                        unitMultiplier = 1000,
                                        value = _currentPower
                                    }
                                }
                            }
                        }
                    }
                };

                var message = JsonSerializer.Serialize(new object[]
                {
                    2,
                    messageId,
                    "TransactionEvent",
                    payload
                });

                SendMessage(message);
                Console.WriteLine($"💸 [{ChargerId}] TransactionEvent 전송 ({eventType}): {_energyAccumulated:F2} kWh");
            }
            catch (Exception ex)
            {
                OnError?.Invoke(this, ex);
            }
        }

        /// <summary>
        /// StatusNotification 전송
        /// </summary>
        public async Task SendStatusNotificationAsync()
        {
            try
            {
                var messageId = Guid.NewGuid().ToString("N").Substring(0, 12);
                var currentTime = DateTime.UtcNow.ToString("o");

                var payload = new
                {
                    timestamp = currentTime,
                    connectorStatus = _currentStatus.ToString(),
                    evseId = 1,
                    connectorId = 1
                };

                var message = JsonSerializer.Serialize(new object[]
                {
                    2,
                    messageId,
                    "StatusNotification",
                    payload
                });

                SendMessage(message);
                Console.WriteLine($"📊 [{ChargerId}] StatusNotification 전송: {_currentStatus}");
            }
            catch (Exception ex)
            {
                OnError?.Invoke(this, ex);
            }
        }

        /// <summary>
        /// 메시지 전송
        /// </summary>
        private void SendMessage(string message)
        {
            if (_isConnected && _webSocket?.IsAlive == true)
            {
                _webSocket.Send(message);
                OnMessageSent?.Invoke(this, message);
            }
        }

        /// <summary>
        /// WebSocket 메시지 수신
        /// </summary>
        private void OnWebSocketMessage(object sender, MessageEventArgs e)
        {
            try
            {
                OnMessageReceived?.Invoke(this, e.Data);
                Console.WriteLine($"📥 [{ChargerId}] 메시지 수신: {e.Data}");

                // OCPP 메시지 파싱 및 처리
                var jsonArray = JsonSerializer.Deserialize<JsonElement>(e.Data);
                if (jsonArray.ValueKind == JsonValueKind.Array && jsonArray.GetArrayLength() >= 2)
                {
                    int messageType = jsonArray[0].GetInt32();
                    string messageId = jsonArray[1].GetString();

                    if (messageType == 3) // CALLRESULT
                    {
                        Console.WriteLine($"✅ [{ChargerId}] CALLRESULT 수신: {messageId}");
                    }
                    else if (messageType == 2) // CALL
                    {
                        string action = jsonArray[2].GetString();
                        var payload = jsonArray[3];

                        HandleIncomingCall(action, messageId, payload);
                    }
                }
            }
            catch (Exception ex)
            {
                OnError?.Invoke(this, ex);
            }
        }

        /// <summary>
        /// 서버의 CALL 메시지 처리
        /// </summary>
        private async void HandleIncomingCall(string action, string messageId, JsonElement payload)
        {
            Console.WriteLine($"🔔 [{ChargerId}] CALL 수신: {action}");

            switch (action)
            {
                case "RequestStartTransaction":
                    await HandleRequestStartTransaction(messageId, payload);
                    break;

                case "RequestStopTransaction":
                    await HandleRequestStopTransaction(messageId);
                    break;

                case "SetChargingProfile":
                    await HandleSetChargingProfile(messageId, payload);
                    break;

                case "GetVariables":
                    await HandleGetVariables(messageId, payload);
                    break;

                default:
                    Console.WriteLine($"⚠️ [{ChargerId}] 미지원 action: {action}");
                    SendCallResult(messageId, new { status = "Rejected" });
                    break;
            }
        }

        /// <summary>
        /// RequestStartTransaction 처리
        /// </summary>
        private async Task HandleRequestStartTransaction(string messageId, JsonElement payload)
        {
            try
            {
                var idToken = payload.GetProperty("idToken").GetString();
                Console.WriteLine($"🔑 [{ChargerId}] RequestStartTransaction: {idToken}");

                // 응답 전송
                SendCallResult(messageId, new { status = "Accepted" });

                // 충전 시작
                await StartChargingAsync(idToken);
            }
            catch (Exception ex)
            {
                OnError?.Invoke(this, ex);
                SendCallResult(messageId, new { status = "Rejected" });
            }
        }

        /// <summary>
        /// RequestStopTransaction 처리
        /// </summary>
        private async Task HandleRequestStopTransaction(string messageId)
        {
            try
            {
                Console.WriteLine($"⏹️ [{ChargerId}] RequestStopTransaction");
                SendCallResult(messageId, new { status = "Accepted" });
                await StopChargingAsync();
            }
            catch (Exception ex)
            {
                OnError?.Invoke(this, ex);
                SendCallResult(messageId, new { status = "Rejected" });
            }
        }

        /// <summary>
        /// SetChargingProfile 처리
        /// </summary>
        private Task HandleSetChargingProfile(string messageId, JsonElement payload)
        {
            try
            {
                var maxPower = payload.GetProperty("chargingSchedule")
                    .GetProperty("chargingSchedulePeriod")[0]
                    .GetProperty("limit")
                    .GetDouble();

                _currentPower = Math.Min(maxPower, _maxPower);
                Console.WriteLine($"⚡ [{ChargerId}] 충전 프로필 설정: {_currentPower}kW");

                SendCallResult(messageId, new { status = "Accepted" });
            }
            catch (Exception ex)
            {
                OnError?.Invoke(this, ex);
                SendCallResult(messageId, new { status = "Rejected" });
            }

            return Task.CompletedTask;
        }

        /// <summary>
        /// GetVariables 처리
        /// </summary>
        private Task HandleGetVariables(string messageId, JsonElement payload)
        {
            try
            {
                var variables = new
                {
                    variableData = new[]
                    {
                        new
                        {
                            variableName = "State",
                            value = _currentStatus.ToString()
                        },
                        new
                        {
                            variableName = "Power",
                            value = _currentPower.ToString()
                        },
                        new
                        {
                            variableName = "EnergyAccumulated",
                            value = _energyAccumulated.ToString("F2")
                        }
                    }
                };

                SendCallResult(messageId, variables);
            }
            catch (Exception ex)
            {
                OnError?.Invoke(this, ex);
                SendCallResult(messageId, new { status = "Rejected" });
            }

            return Task.CompletedTask;
        }

        /// <summary>
        /// CALLRESULT 전송
        /// </summary>
        private void SendCallResult(string messageId, object payload)
        {
            var message = JsonSerializer.Serialize(new object[]
            {
                3, // CALLRESULT 메시지 타입
                messageId,
                payload
            });

            SendMessage(message);
            Console.WriteLine($"📤 [{ChargerId}] CALLRESULT 전송: {messageId}");
        }

        /// <summary>
        /// WebSocket 오류 처리
        /// </summary>
        private void OnWebSocketError(object sender, ErrorEventArgs e)
        {
            var error = new Exception(e.Message);
            OnError?.Invoke(this, error);
            Console.WriteLine($"❌ [{ChargerId}] WebSocket 오류: {e.Message}");
        }

        /// <summary>
        /// WebSocket 종료 처리
        /// </summary>
        private void OnWebSocketClose(object sender, CloseEventArgs e)
        {
            _isConnected = false;
            Console.WriteLine($"🔌 [{ChargerId}] 연결 종료: {e.Code}");
        }

        /// <summary>
        /// 연결 해제
        /// </summary>
        public void Disconnect()
        {
            _isConnected = false;
            _webSocket?.Close();
            Console.WriteLine($"👋 [{ChargerId}] 연결 해제");
        }

        /// <summary>
        /// 현재 상태 조회
        /// </summary>
        public string GetStatus()
        {
            return $"[{ChargerId}] 상태: {_currentStatus}, 전력: {_currentPower}kW, 누적: {_energyAccumulated:F2}kWh";
        }
    }

    /// <summary>
    /// 통합 테스트 프로그램
    /// </summary>
    public class Program
    {
        static async Task Main(string[] args)
        {
            Console.OutputEncoding = System.Text.Encoding.UTF8;
            Console.WriteLine("=".PadRight(80, '='));
            Console.WriteLine("  OCPP 2.0.1 C# 충전기 시뮬레이터");
            Console.WriteLine("=".PadRight(80, '='));
            Console.WriteLine();

            // 여러 충전기 생성
            var charger1 = new ChargerSimulator(
                "emart_jeju_01",
                "ws://localhost:9000",
                "ABB Terra 53",
                "ABB");

            var charger2 = new ChargerSimulator(
                "emart_shinjeju_01",
                "ws://localhost:9000",
                "Siemens VersiCharge",
                "Siemens");

            try
            {
                // 충전기 연결
                Console.WriteLine("[1단계] 충전기 연결");
                Console.WriteLine("-".PadRight(80, '-'));
                await charger1.ConnectAsync();
                await Task.Delay(2000);
                await charger2.ConnectAsync();
                await Task.Delay(3000);

                // 충전기 상태 확인
                Console.WriteLine("\n[2단계] 충전기 상태 확인");
                Console.WriteLine("-".PadRight(80, '-'));
                Console.WriteLine(charger1.GetStatus());
                Console.WriteLine(charger2.GetStatus());
                await Task.Delay(2000);

                // 충전 시작
                Console.WriteLine("\n[3단계] 충전 시작");
                Console.WriteLine("-".PadRight(80, '-'));
                await charger1.StartChargingAsync("token_user_001");
                await Task.Delay(3000);
                await charger2.StartChargingAsync("token_user_002");
                await Task.Delay(5000);

                // 충전 중 상태 확인
                Console.WriteLine("\n[4단계] 충전 진행 상황");
                Console.WriteLine("-".PadRight(80, '-'));
                Console.WriteLine(charger1.GetStatus());
                Console.WriteLine(charger2.GetStatus());
                await Task.Delay(10000);

                // 상태 업데이트
                Console.WriteLine("\n[5단계] StatusNotification 전송");
                Console.WriteLine("-".PadRight(80, '-'));
                await charger1.SendStatusNotificationAsync();
                await charger2.SendStatusNotificationAsync();
                await Task.Delay(3000);

                // 충전 중지
                Console.WriteLine("\n[6단계] 충전 중지");
                Console.WriteLine("-".PadRight(80, '-'));
                await charger1.StopChargingAsync();
                await Task.Delay(2000);
                await charger2.StopChargingAsync();
                await Task.Delay(3000);

                // 최종 상태
                Console.WriteLine("\n[7단계] 최종 상태");
                Console.WriteLine("-".PadRight(80, '-'));
                Console.WriteLine(charger1.GetStatus());
                Console.WriteLine(charger2.GetStatus());

                Console.WriteLine("\n✅ 모든 테스트 완료!");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"\n❌ 오류 발생: {ex.Message}");
            }
            finally
            {
                charger1?.Disconnect();
                charger2?.Disconnect();
                Console.WriteLine("\n프로그램 종료...");
            }
        }
    }
}
