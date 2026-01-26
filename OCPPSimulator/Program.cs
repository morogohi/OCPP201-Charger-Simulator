using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using OCPPSimulator.Clients;
using OCPPSimulator.Models;

namespace OCPPSimulator;

/// <summary>
/// OCPP 시뮬레이션 테스트 시나리오
/// </summary>
public class TestScenarios
{
    /// <summary>
    /// 시나리오 1: 기본 연결 및 BootNotification
    /// </summary>
    public static async Task TestScenario1Async()
    {
        Console.WriteLine("\n" + new string('=', 80));
        Console.WriteLine("[테스트 시나리오 1] 기본 연결 및 BootNotification");
        Console.WriteLine(new string('=', 80));

        using var charger = new OCPPClient("emart_jeju_01");
        await charger.ConnectAsync();
        await Task.Delay(5000);

        Console.WriteLine(charger.GetStatus());
        await charger.DisconnectAsync();
    }

    /// <summary>
    /// 시나리오 2: 충전 세션 (시작 -> 충전 -> 중지)
    /// </summary>
    public static async Task TestScenario2Async()
    {
        Console.WriteLine("\n" + new string('=', 80));
        Console.WriteLine("[테스트 시나리오 2] 충전 세션 (에너지 추적)");
        Console.WriteLine(new string('=', 80));

        using var charger = new OCPPClient("emart_jeju_01", maxPower: 100);
        await charger.ConnectAsync();
        await Task.Delay(2000);

        // 충전 시작
        await charger.StartChargingAsync("token_user_001");
        await Task.Delay(15000); // 15초 충전

        // 충전 중지
        await charger.StopChargingAsync();
        await Task.Delay(2000);

        Console.WriteLine(charger.GetStatus());
        await charger.DisconnectAsync();
    }

    /// <summary>
    /// 시나리오 3: 다중 충전기 동시 운영
    /// </summary>
    public static async Task TestScenario3Async()
    {
        Console.WriteLine("\n" + new string('=', 80));
        Console.WriteLine("[테스트 시나리오 3] 다중 충전기 동시 운영");
        Console.WriteLine(new string('=', 80));

        var chargers = new List<OCPPClient>
        {
            new OCPPClient("emart_jeju_01", maxPower: 100),
            new OCPPClient("emart_jeju_02", maxPower: 100),
            new OCPPClient("emart_shinjeju_01", maxPower: 50),
        };

        // 모든 충전기 연결
        var connectTasks = new List<Task>();
        foreach (var charger in chargers)
        {
            connectTasks.Add(charger.ConnectAsync());
        }
        await Task.WhenAll(connectTasks);

        await Task.Delay(3000);

        // 모든 충전기에서 충전 시작
        var startTasks = new List<Task>();
        foreach (var charger in chargers)
        {
            startTasks.Add(charger.StartChargingAsync("token_multi_001"));
        }
        await Task.WhenAll(startTasks);

        // 20초 동안 충전 시뮬레이션
        await Task.Delay(20000);

        // 모든 충전기에서 충전 중지
        var stopTasks = new List<Task>();
        foreach (var charger in chargers)
        {
            stopTasks.Add(charger.StopChargingAsync());
        }
        await Task.WhenAll(stopTasks);

        await Task.Delay(2000);

        // 상태 출력
        Console.WriteLine("\n[최종 상태]");
        foreach (var charger in chargers)
        {
            Console.WriteLine(charger.GetStatus());
        }

        // 연결 해제
        var disconnectTasks = new List<Task>();
        foreach (var charger in chargers)
        {
            disconnectTasks.Add(charger.DisconnectAsync());
        }
        await Task.WhenAll(disconnectTasks);

        // 리소스 정리
        foreach (var charger in chargers)
        {
            charger.Dispose();
        }
    }

    /// <summary>
    /// 시나리오 4: 에너지 데이터 검증
    /// </summary>
    public static async Task TestScenario4Async()
    {
        Console.WriteLine("\n" + new string('=', 80));
        Console.WriteLine("[테스트 시나리오 4] 에너지 데이터 검증");
        Console.WriteLine(new string('=', 80));

        using var charger = new OCPPClient("emart_jeju_01", maxPower: 100);
        await charger.ConnectAsync();
        await Task.Delay(2000);

        // 명시적인 에너지 값으로 충전 시뮬레이션
        Console.WriteLine("\n[에너지 데이터 검증 테스트]");
        
        charger.CurrentStatus = ChargerStatus.Preparing;
        charger.TransactionId = "txn_test_001";
        charger.EnergyAccumulated = 0.0;
        charger.IsCharging = true;

        // Started: 0 kWh
        await charger.SendTransactionEventAsync("Started", "test_user");
        
        await Task.Delay(1000);

        // Updated: 0.5 kWh
        charger.EnergyAccumulated = 0.5;
        charger.CurrentStatus = ChargerStatus.Charging;
        charger.CurrentPower = 100;
        await charger.SendTransactionEventAsync("Updated", "test_user");

        await Task.Delay(1000);

        // Updated: 1.0 kWh
        charger.EnergyAccumulated = 1.0;
        await charger.SendTransactionEventAsync("Updated", "test_user");

        await Task.Delay(1000);

        // Updated: 1.5 kWh
        charger.EnergyAccumulated = 1.5;
        await charger.SendTransactionEventAsync("Updated", "test_user");

        await Task.Delay(1000);

        // Ended: 1.5 kWh (final)
        charger.CurrentStatus = ChargerStatus.Finishing;
        await charger.SendTransactionEventAsync("Ended", "test_user");

        Console.WriteLine("\n[테스트 완료]");
        await charger.DisconnectAsync();
    }

    /// <summary>
    /// 스트레스 테스트: 여러 거래 반복
    /// </summary>
    public static async Task TestStressAsync(int transactionCount = 5)
    {
        Console.WriteLine("\n" + new string('=', 80));
        Console.WriteLine($"[스트레스 테스트] {transactionCount}개 거래 반복");
        Console.WriteLine(new string('=', 80));

        using var charger = new OCPPClient("emart_jeju_01", maxPower: 100);
        await charger.ConnectAsync();
        await Task.Delay(2000);

        for (int i = 0; i < transactionCount; i++)
        {
            Console.WriteLine($"\n--- 거래 {i + 1}/{transactionCount} ---");
            
            await charger.StartChargingAsync($"token_{i + 1}");
            await Task.Delay(5000); // 5초 충전

            await charger.StopChargingAsync();
            await Task.Delay(1000);

            Console.WriteLine(charger.GetStatus());
        }

        await charger.DisconnectAsync();
    }
}

/// <summary>
/// 메인 프로그램
/// </summary>
class Program
{
    static async Task Main(string[] args)
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        
        Console.WriteLine("╔════════════════════════════════════════════════════════════════════════════════╗");
        Console.WriteLine("║             OCPP 2.0.1 C# 시뮬레이터 - 테스트 시나리오                          ║");
        Console.WriteLine("╚════════════════════════════════════════════════════════════════════════════════╝");
        Console.WriteLine();
        Console.WriteLine("사용법: OCPPSimulator.exe [시나리오 번호 | all]");
        Console.WriteLine();
        Console.WriteLine("시나리오:");
        Console.WriteLine("  1 - 기본 연결 및 BootNotification");
        Console.WriteLine("  2 - 충전 세션 (시작 -> 충전 -> 중지)");
        Console.WriteLine("  3 - 다중 충전기 동시 운영");
        Console.WriteLine("  4 - 에너지 데이터 검증");
        Console.WriteLine("  5 - 스트레스 테스트 (5개 거래)");
        Console.WriteLine("  all - 모든 시나리오 실행");
        Console.WriteLine();

        string scenarioArg = args.Length > 0 ? args[0] : "1";

        try
        {
            switch (scenarioArg.ToLower())
            {
                case "1":
                    await TestScenarios.TestScenario1Async();
                    break;

                case "2":
                    await TestScenarios.TestScenario2Async();
                    break;

                case "3":
                    await TestScenarios.TestScenario3Async();
                    break;

                case "4":
                    await TestScenarios.TestScenario4Async();
                    break;

                case "5":
                    await TestScenarios.TestStressAsync();
                    break;

                case "all":
                    await TestScenarios.TestScenario1Async();
                    await Task.Delay(3000);
                    
                    await TestScenarios.TestScenario2Async();
                    await Task.Delay(3000);
                    
                    await TestScenarios.TestScenario3Async();
                    await Task.Delay(3000);
                    
                    await TestScenarios.TestScenario4Async();
                    break;

                default:
                    Console.WriteLine("❌ 잘못된 시나리오 번호입니다.");
                    break;
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ 오류 발생: {ex.Message}");
            Console.WriteLine($"스택 트레이스: {ex.StackTrace}");
        }

        Console.WriteLine("\n✅ 테스트 완료!");
    }
}
