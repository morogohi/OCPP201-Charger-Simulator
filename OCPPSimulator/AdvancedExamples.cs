using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Threading.Tasks;
using OCPPSimulator.Clients;

namespace OCPPSimulator;

/// <summary>
/// C# 시뮬레이터 고급 예제
/// </summary>
public class AdvancedExamples
{
    /// <summary>
    /// 예제 1: 커스텀 서버 연결
    /// </summary>
    public static async Task Example1_CustomServerAsync()
    {
        Console.WriteLine("\n[예제 1] 커스텀 서버 연결");
        Console.WriteLine("════════════════════════════════════════════════════════════════");

        // 커스텀 서버 URL 및 전력 설정
        var charger = new OCPPClient(
            chargerId: "custom_charger_001",
            serverUrl: "ws://127.0.0.1:9000",
            maxPower: 150  // 150kW 급속 충전기
        );

        try
        {
            await charger.ConnectAsync();
            Console.WriteLine($"✅ {charger.GetStatus()}");
            await charger.DisconnectAsync();
        }
        finally
        {
            charger.Dispose();
        }
    }

    /// <summary>
    /// 예제 2: 긴 충전 시뮬레이션
    /// </summary>
    public static async Task Example2_LongChargingSessionAsync()
    {
        Console.WriteLine("\n[예제 2] 긴 충전 시뮬레이션 (30초)");
        Console.WriteLine("════════════════════════════════════════════════════════════════");

        using var charger = new OCPPClient("extended_session_01", maxPower: 100);
        
        try
        {
            await charger.ConnectAsync();
            
            Console.WriteLine("⏱️  30초 동안 충전 시뮬레이션 시작...");
            await charger.StartChargingAsync("extended_token");
            
            // 30초 동안 5초마다 상태 출력
            for (int i = 0; i < 6; i++)
            {
                await Task.Delay(5000);
                Console.WriteLine($"  [{i * 5}초] {charger.GetStatus()}");
            }
            
            await charger.StopChargingAsync();
            Console.WriteLine($"✅ 최종 상태: {charger.GetStatus()}");
        }
        finally
        {
            await charger.DisconnectAsync();
        }
    }

    /// <summary>
    /// 예제 3: 급속 충전 vs 완속 충전 비교
    /// </summary>
    public static async Task Example3_ChargerComparisonAsync()
    {
        Console.WriteLine("\n[예제 3] 급속 충전 vs 완속 충전 비교");
        Console.WriteLine("════════════════════════════════════════════════════════════════");

        // 급속 충전기 (350kW)
        var fastCharger = new OCPPClient("fast_charger_001", maxPower: 350);
        
        // 완속 충전기 (22kW)
        var slowCharger = new OCPPClient("slow_charger_001", maxPower: 22);

        try
        {
            await fastCharger.ConnectAsync();
            await slowCharger.ConnectAsync();

            Console.WriteLine("\n🚀 동시에 충전 시작...");
            
            var startTasks = new[]
            {
                fastCharger.StartChargingAsync("fast_token"),
                slowCharger.StartChargingAsync("slow_token")
            };
            await Task.WhenAll(startTasks);

            // 10초 충전
            for (int i = 0; i < 2; i++)
            {
                await Task.Delay(5000);
                Console.WriteLine($"\n[{i * 5 + 5}초]");
                Console.WriteLine($"  급속: {fastCharger.GetStatus()}");
                Console.WriteLine($"  완속: {slowCharger.GetStatus()}");
            }

            Console.WriteLine("\n⏹️  충전 중지...");
            var stopTasks = new[]
            {
                fastCharger.StopChargingAsync(),
                slowCharger.StopChargingAsync()
            };
            await Task.WhenAll(stopTasks);

            Console.WriteLine("\n[최종 비교]");
            Console.WriteLine($"급속 충전기:");
            Console.WriteLine($"  {fastCharger.GetStatus()}");
            Console.WriteLine($"완속 충전기:");
            Console.WriteLine($"  {slowCharger.GetStatus()}");
            
            double ratio = fastCharger.EnergyAccumulated / slowCharger.EnergyAccumulated;
            Console.WriteLine($"\n⚡ 에너지 충전 비율: {ratio:F2}x");
        }
        finally
        {
            await fastCharger.DisconnectAsync();
            await slowCharger.DisconnectAsync();
            fastCharger.Dispose();
            slowCharger.Dispose();
        }
    }

    /// <summary>
    /// 예제 4: 충전소 (Station) 시뮬레이션
    /// </summary>
    public static async Task Example4_ChargingStationAsync()
    {
        Console.WriteLine("\n[예제 4] 충전소 시뮬레이션 (5개 충전기)");
        Console.WriteLine("════════════════════════════════════════════════════════════════");

        var station = new ChargingStation("jeju_emart_station", 5);
        
        try
        {
            Console.WriteLine($"🏢 {station.Name} 초기화 중...");
            await station.InitializeAsync();

            Console.WriteLine("\n📊 충전소 상태:");
            station.PrintStatus();

            Console.WriteLine("\n🚗 랜덤 충전 요청 시뮬레이션...");
            await station.SimulateRandomLoadAsync(duration: 15000);

            Console.WriteLine("\n📊 최종 충전소 상태:");
            station.PrintStatus();

            var stats = station.GetStatistics();
            Console.WriteLine("\n📈 통계:");
            Console.WriteLine($"  총 에너지: {stats.TotalEnergy:F2} kWh");
            Console.WriteLine($"  총 비용: {stats.TotalCost:F0} 원");
            Console.WriteLine($"  평균 충전: {stats.AverageEnergy:F2} kWh");
            Console.WriteLine($"  최대 충전: {stats.MaxEnergy:F2} kWh");
        }
        finally
        {
            await station.ShutdownAsync();
        }
    }

    /// <summary>
    /// 예제 5: 성능 벤치마크
    /// </summary>
    public static async Task Example5_PerformanceBenchmarkAsync()
    {
        Console.WriteLine("\n[예제 5] 성능 벤치마크");
        Console.WriteLine("════════════════════════════════════════════════════════════════");

        const int chargerCount = 50;
        const int transactionCount = 3;

        Console.WriteLine($"⏱️  {chargerCount}개 충전기에서 {transactionCount}개 거래 실행");
        Console.WriteLine("════════════════════════════════════════════════════════════════");

        var chargers = Enumerable.Range(1, chargerCount)
            .Select(i => new OCPPClient($"benchmark_charger_{i:D3}", maxPower: 100))
            .ToList();

        var stopwatch = Stopwatch.StartNew();

        try
        {
            // 연결
            Console.WriteLine("\n[1/3] 모든 충전기 연결 중...");
            var connectTasks = chargers.Select(c => c.ConnectAsync()).ToList();
            await Task.WhenAll(connectTasks);
            Console.WriteLine($"✅ {chargerCount}개 충전기 연결 완료");

            // 거래 실행
            Console.WriteLine($"\n[2/3] {transactionCount}개 거래 실행 중...");
            for (int t = 0; t < transactionCount; t++)
            {
                Console.WriteLine($"\n거래 {t + 1}/{transactionCount}:");
                
                // 충전 시작
                var startTasks = chargers.Select(c => c.StartChargingAsync($"token_{t}")).ToList();
                await Task.WhenAll(startTasks);
                
                // 5초 충전
                await Task.Delay(5000);
                
                // 충전 중지
                var stopTasks = chargers.Select(c => c.StopChargingAsync()).ToList();
                await Task.WhenAll(stopTasks);

                double roundTotalEnergy = chargers.Sum(c => c.EnergyAccumulated);
                Console.WriteLine($"  누적 에너지: {roundTotalEnergy:F2} kWh");
            }

            // 결과 분석
            Console.WriteLine($"\n[3/3] 결과 분석");
            Console.WriteLine("════════════════════════════════════════════════════════════════");

            double totalEnergy = chargers.Sum(c => c.EnergyAccumulated);
            double avgEnergy = chargers.Average(c => c.EnergyAccumulated);
            double maxEnergy = chargers.Max(c => c.EnergyAccumulated);
            double minEnergy = chargers.Min(c => c.EnergyAccumulated);

            Console.WriteLine($"\n📊 결과:");
            Console.WriteLine($"  총 에너지: {totalEnergy:F2} kWh");
            Console.WriteLine($"  평균 에너지: {avgEnergy:F2} kWh");
            Console.WriteLine($"  최대 에너지: {maxEnergy:F2} kWh");
            Console.WriteLine($"  최소 에너지: {minEnergy:F2} kWh");

            stopwatch.Stop();
            Console.WriteLine($"\n⏱️  총 시간: {stopwatch.ElapsedMilliseconds}ms ({stopwatch.Elapsed.TotalSeconds:F2}초)");
            Console.WriteLine($"처리량: {(chargerCount * transactionCount) / stopwatch.Elapsed.TotalSeconds:F2} 거래/초");
            Console.WriteLine($"메시지: {chargers.Count * transactionCount * 2 / stopwatch.Elapsed.TotalSeconds:F0} 메시지/초");
        }
        finally
        {
            // 연결 해제
            Console.WriteLine("\n[정리] 연결 해제 중...");
            var disconnectTasks = chargers.Select(c => c.DisconnectAsync()).ToList();
            await Task.WhenAll(disconnectTasks);

            foreach (var charger in chargers)
            {
                charger.Dispose();
            }
        }
    }

    /// <summary>
    /// 예제 6: 에러 처리 및 복구
    /// </summary>
    public static async Task Example6_ErrorHandlingAsync()
    {
        Console.WriteLine("\n[예제 6] 에러 처리 및 재연결");
        Console.WriteLine("════════════════════════════════════════════════════════════════");

        var charger = new OCPPClient("error_handling_01", maxPower: 100);

        // 잘못된 서버에 연결 시도
        Console.WriteLine("⚠️  잘못된 서버에 연결 시도...");
        var failedCharger = new OCPPClient(
            "failed_01",
            serverUrl: "ws://invalid.server:9999",
            maxPower: 100
        );
        try
        {
            var cts = new System.Threading.CancellationTokenSource(TimeSpan.FromSeconds(5));
            await failedCharger.ConnectAsync();
        }
        catch (OperationCanceledException)
        {
            Console.WriteLine("❌ 연결 타임아웃 (예상된 결과)");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ 연결 오류: {ex.Message}");
        }

        failedCharger.Dispose();

        // 올바른 서버에 연결
        Console.WriteLine("\n✅ 올바른 서버에 연결 시도...");
        try
        {
            await charger.ConnectAsync();
            Console.WriteLine($"✅ 연결 성공: {charger.GetStatus()}");
            await charger.DisconnectAsync();
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ 연결 실패: {ex.Message}");
        }
        finally
        {
            charger.Dispose();
        }
    }
}

/// <summary>
/// 충전소 클래스 (여러 충전기 관리)
/// </summary>
public class ChargingStation
{
    private readonly List<OCPPClient> _chargers;
    public string Name { get; set; }

    public ChargingStation(string name, int chargerCount)
    {
        Name = name;
        _chargers = Enumerable.Range(1, chargerCount)
            .Select(i => new OCPPClient($"{name}_charger_{i:D2}", maxPower: 100))
            .ToList();
    }

    public async Task InitializeAsync()
    {
        var connectTasks = _chargers.Select(c => c.ConnectAsync()).ToList();
        await Task.WhenAll(connectTasks);
    }

    public async Task ShutdownAsync()
    {
        var disconnectTasks = _chargers.Select(c => c.DisconnectAsync()).ToList();
        await Task.WhenAll(disconnectTasks);

        foreach (var charger in _chargers)
        {
            charger.Dispose();
        }
    }

    public void PrintStatus()
    {
        Console.WriteLine($"충전소: {Name}");
        foreach (var charger in _chargers)
        {
            Console.WriteLine($"  {charger.GetStatus()}");
        }
    }

    public async Task SimulateRandomLoadAsync(int duration)
    {
        var startTime = DateTime.UtcNow;
        var random = new Random();

        while (DateTime.UtcNow - startTime < TimeSpan.FromMilliseconds(duration))
        {
            var availableChargers = _chargers.Where(c => !c.IsCharging).ToList();
            
            if (availableChargers.Count > 0)
            {
                var charger = availableChargers[random.Next(availableChargers.Count)];
                _ = charger.StartChargingAsync($"random_token_{Guid.NewGuid().ToString()[..8]}");
            }

            await Task.Delay(1000);
        }

        // 모든 충전 중지
        var stopTasks = _chargers.Where(c => c.IsCharging)
            .Select(c => c.StopChargingAsync())
            .ToList();
        await Task.WhenAll(stopTasks);
    }

    public (double TotalEnergy, double TotalCost, double AverageEnergy, double MaxEnergy) GetStatistics()
    {
        double total = _chargers.Sum(c => c.EnergyAccumulated);
        double cost = total * 150;
        double avg = _chargers.Average(c => c.EnergyAccumulated);
        double max = _chargers.Max(c => c.EnergyAccumulated);

        return (total, cost, avg, max);
    }
}

/// <summary>
/// 고급 예제 실행
/// </summary>
public static class AdvancedExamplesRunner
{
    public static async Task RunAsync(string exampleNumber)
    {
        try
        {
            switch (exampleNumber)
            {
                case "1":
                    await AdvancedExamples.Example1_CustomServerAsync();
                    break;

                case "2":
                    await AdvancedExamples.Example2_LongChargingSessionAsync();
                    break;

                case "3":
                    await AdvancedExamples.Example3_ChargerComparisonAsync();
                    break;

                case "4":
                    await AdvancedExamples.Example4_ChargingStationAsync();
                    break;

                case "5":
                    await AdvancedExamples.Example5_PerformanceBenchmarkAsync();
                    break;

                case "6":
                    await AdvancedExamples.Example6_ErrorHandlingAsync();
                    break;

                default:
                    Console.WriteLine("❌ 유효하지 않은 예제 번호입니다.");
                    break;
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"\n❌ 오류 발생: {ex.Message}");
            Console.WriteLine($"스택 트레이스: {ex.StackTrace}");
        }
    }
}
