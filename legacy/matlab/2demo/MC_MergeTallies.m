function total = MC_MergeTallies(total, packet)
    % 先合并原始权重，最后只做一次归一化。
    [indices, ~, values] = find(packet.Araw);
    total.Araw(indices) = total.Araw(indices) + values;
    [indices, ~, values] = find(packet.AirPathRaw);
    total.AirPathRaw(indices) = total.AirPathRaw(indices) + values;
    total.Rraw = total.Rraw + packet.Rraw;
    total.Traw = total.Traw + packet.Traw;
    names = {'sideEscapeRaw', 'rouletteBalanceRaw', 'Nlaunched', ...
        'Nterminated', 'boundaryEvents', 'scatteringEvents', 'airEscapedPackets'};
    for k = 1:numel(names)
        name = names{k};
        total.(name) = total.(name) + packet.(name);
    end
end
