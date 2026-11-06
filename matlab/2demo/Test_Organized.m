function report = Test_Organized()
    % 原脚本衔接、组织模型和数值核验；测试不会保存模拟文件。
    [model, tissue, config, tallies] = Prepare_Inputs(50, true, 1);
    assert(isequal(model.size, [40, 40, 40]));
    assert(model.T(20, 20, 20) == 3);
    assert(model.T(20, 20, 11) == 5);
    assert(model.T(20, 20, 1) == 1);
    assert(config.Nphotons == 50);
    assert(tissue(3).mua == 11.2);
    assert(all(tallies.Araw(:) == 0));

    [remaining, absorbed] = Step7_Drop(0.8, 2, 0.3);
    assert(abs(remaining + absorbed - 0.8) < 1e-14);
    [~, lengths] = Step6_AirTrack( ...
        [0.005, 0.005, 1], [0.6, 0, -0.8], 0.7, [21, 21, 10], model);
    assert(abs(sum(lengths) - 0.875) < 1e-12);

    a = Step4_Main(50, true, 1, false);
    b = Step4_Main(50, true, 1, false);
    assert(isequaln(a.Phi, b.Phi));
    assert(a.airEscapedPackets > 0);
    assert(abs(a.bookkeepingTotal - 1) < 1e-8);
    report = struct('inputScripts', true, 'bloodVessel', true, ...
        'drop', true, 'airPaths', true, 'reproducibility', true, ...
        'energy', true);
    disp('ORGANIZED_TESTS_PASSED');
end
