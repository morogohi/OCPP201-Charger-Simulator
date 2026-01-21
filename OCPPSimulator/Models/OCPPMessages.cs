using System;
using System.Text.Json.Serialization;

namespace OCPPSimulator.Models;

/// <summary>
/// OCPP 2.0.1 메시지 타입
/// </summary>
public enum MessageType
{
    CALL = 2,
    CALLRESULT = 3,
    CALLERROR = 4
}

/// <summary>
/// 충전기 상태
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
/// OCPP CALL 메시지
/// [MessageType, UniqueId, Action, Payload]
/// </summary>
public class OCPPCallMessage
{
    [JsonPropertyName("messageType")]
    public int MessageType { get; set; } = (int)Models.MessageType.CALL;

    [JsonPropertyName("messageId")]
    public string MessageId { get; set; } = "";

    [JsonPropertyName("action")]
    public string Action { get; set; } = "";

    [JsonPropertyName("payload")]
    public object Payload { get; set; } = new { };
}

/// <summary>
/// OCPP CALLRESULT 메시지
/// [MessageType, UniqueId, Payload]
/// </summary>
public class OCPPCallResultMessage
{
    [JsonPropertyName("messageType")]
    public int MessageType { get; set; } = (int)Models.MessageType.CALLRESULT;

    [JsonPropertyName("messageId")]
    public string MessageId { get; set; } = "";

    [JsonPropertyName("payload")]
    public object Payload { get; set; } = new { };
}

/// <summary>
/// BootNotification 요청
/// </summary>
public class BootNotificationRequest
{
    [JsonPropertyName("chargingStation")]
    public ChargingStationInfo? ChargingStation { get; set; }

    [JsonPropertyName("reason")]
    public string Reason { get; set; } = "PowerUp";
}

/// <summary>
/// 충전기 정보
/// </summary>
public class ChargingStationInfo
{
    [JsonPropertyName("model")]
    public string Model { get; set; } = "CSharpSimulator";

    [JsonPropertyName("vendorName")]
    public string VendorName { get; set; } = "OCPP.NET";

    [JsonPropertyName("serialNumber")]
    public string SerialNumber { get; set; } = "";

    [JsonPropertyName("firmwareVersion")]
    public string FirmwareVersion { get; set; } = "1.0.0";
}

/// <summary>
/// TransactionEvent 요청
/// </summary>
public class TransactionEventRequest
{
    [JsonPropertyName("eventType")]
    public string EventType { get; set; } = "Updated";

    [JsonPropertyName("timestamp")]
    public string Timestamp { get; set; } = DateTime.UtcNow.ToString("O") + "Z";

    [JsonPropertyName("triggerReason")]
    public string TriggerReason { get; set; } = "Authorized";

    [JsonPropertyName("seqNo")]
    public int SeqNo { get; set; } = 0;

    [JsonPropertyName("transactionData")]
    public TransactionData? TransactionData { get; set; }
}

/// <summary>
/// 거래 데이터
/// </summary>
public class TransactionData
{
    [JsonPropertyName("transactionId")]
    public string TransactionId { get; set; } = "";

    [JsonPropertyName("chargingState")]
    public string ChargingState { get; set; } = "Charging";

    [JsonPropertyName("timeSpentCharging")]
    public int TimeSpentCharging { get; set; } = 0;

    [JsonPropertyName("stoppedReason")]
    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public string? StoppedReason { get; set; }

    [JsonPropertyName("totalCost")]
    public decimal TotalCost { get; set; } = 0;

    [JsonPropertyName("chargingPeriods")]
    public List<ChargingPeriod>? ChargingPeriods { get; set; } = new();
}

/// <summary>
/// 충전 기간
/// </summary>
public class ChargingPeriod
{
    [JsonPropertyName("startDateTime")]
    public string StartDateTime { get; set; } = DateTime.UtcNow.ToString("O") + "Z";

    [JsonPropertyName("dimensions")]
    public List<Dimension>? Dimensions { get; set; } = new();
}

/// <summary>
/// 에너지/전력 차원
/// </summary>
public class Dimension
{
    [JsonPropertyName("name")]
    public string Name { get; set; } = "";

    [JsonPropertyName("unit")]
    public string Unit { get; set; } = "Wh";

    [JsonPropertyName("unitMultiplier")]
    public int UnitMultiplier { get; set; } = 1;

    [JsonPropertyName("value")]
    public decimal Value { get; set; } = 0;
}

/// <summary>
/// Heartbeat 요청
/// </summary>
public class HeartbeatRequest
{
    [JsonPropertyName("currentTime")]
    public string CurrentTime { get; set; } = DateTime.UtcNow.ToString("O") + "Z";
}

/// <summary>
/// StatusNotification 요청
/// </summary>
public class StatusNotificationRequest
{
    [JsonPropertyName("timestamp")]
    public string Timestamp { get; set; } = DateTime.UtcNow.ToString("O") + "Z";

    [JsonPropertyName("connectorStatus")]
    public string ConnectorStatus { get; set; } = "Available";

    [JsonPropertyName("evseId")]
    public int EvseId { get; set; } = 1;

    [JsonPropertyName("connectorId")]
    public int ConnectorId { get; set; } = 1;
}
