function packet = MC_RunBatch(modelInput, tissue, config, photonCount, batchID)
    % 独立随机子流；工作进程只计算，不写文件、不画图。
    %执行其中一批光子的发射、传播、吸收、散射和逃逸。
    fprintf("11111111111 用到了")
    if isa(modelInput, 'parallel.pool.Constant')
        model = modelInput.Value;
    else
        model = modelInput;
    end
    previousStream = RandStream.getGlobalStream;
    restoreStream = onCleanup(@() RandStream.setGlobalStream(previousStream));
    stream = RandStream('mrg32k3a', 'Seed', config.seed);
    stream.Substream = batchID;
    RandStream.setGlobalStream(stream);
    tallies = MC_CreateTallies(model);
    for iphoton = 1:photonCount
        photon = Step4_Launch(config.source, model);
        tallies.Nlaunched = tallies.Nlaunched + 1;
        while photon.alive
            [photon, deposits, event, nBoundary] = Step5_Hop(photon, model, tissue);
            for k = 1:numel(deposits.indices)
                j = deposits.indices(k);
                tallies.Araw(j) = tallies.Araw(j) + deposits.weights(k);
                tallies.AirPathRaw(j)=tallies.AirPathRaw(j)+deposits.airLengths(k);
            end
            tallies.boundaryEvents = tallies.boundaryEvents + nBoundary;
            switch event.kind
                case 'top'
                    j = event.surfaceIndex;
                    tallies.Rraw(j) = tallies.Rraw(j) + event.weight;
                case 'bottom'
                    j = event.surfaceIndex;
                    tallies.Traw(j) = tallies.Traw(j) + event.weight;
                case 'side'
                    tallies.sideEscapeRaw = tallies.sideEscapeRaw + event.weight;
            end
            if ~isempty(event.airIndices)
                tallies.airEscapedPackets = tallies.airEscapedPackets + 1;
                for k = 1:numel(event.airIndices)
                    j = event.airIndices(k);
                    tallies.AirPathRaw(j) = tallies.AirPathRaw(j) + event.airWeights(k);
                end
            end
            if photon.alive
                [photon, correction] = Step8_SpinCheck(photon, tissue, config.roulette);
                tallies.scatteringEvents = tallies.scatteringEvents + 1;
                tallies.rouletteBalanceRaw = tallies.rouletteBalanceRaw + correction;
            end
        end
        tallies.Nterminated = tallies.Nterminated + 1;
    end
    % 只返回非零体素，减少进程间传输及等待结果的内存。
    tallies.Araw = sparse(tallies.Araw(:));
    tallies.AirPathRaw = sparse(tallies.AirPathRaw(:));
    packet = tallies;
    clear restoreStream;
end
