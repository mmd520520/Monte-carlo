function tallies = MC_CreateTallies(model)
    % 每批独立分配累计数组，批内不共享可写数据。
    % 为每批计算创建空的统计数组，记录吸收、反射、透射等。
    tallies.Araw = zeros(model.size);
    tallies.Rraw = zeros(model.Nx, model.Ny);
    tallies.Traw = zeros(model.Nx, model.Ny);
    tallies.AirPathRaw = zeros(model.size);
    tallies.sideEscapeRaw = 0;
    tallies.rouletteBalanceRaw = 0;
    tallies.Nlaunched = 0;
    tallies.Nterminated = 0;
    tallies.boundaryEvents = 0;
    tallies.scatteringEvents = 0;
    tallies.airEscapedPackets = 0;
end
