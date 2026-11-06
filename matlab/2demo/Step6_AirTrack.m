function [indices, weightedLengths] = Step6_AirTrack(position, direction, weight, airIdx, model)
    % 空气直线传播。返回经过体素的线性索引及W*路径长度，不修改大数组。
    indices = zeros(128, 1);
    weightedLengths = zeros(128, 1);
    count = 0;
    while all(airIdx >= 1 & airIdx <= [model.Nx model.Ny model.airLayerCount])
        lo = (airIdx-1).*model.spacing-model.offset;
        hi = airIdx.*model.spacing-model.offset;
        distances = inf(1, 3);
        pos = direction > 0;
        neg = direction < 0;
        distances(pos) = (hi(pos)-position(pos))./direction(pos);
        distances(neg) = (lo(neg)-position(neg))./direction(neg);
        assert(all(distances >= -1e-8), '空气光子偏离当前体素。');
        [len, axisID] = min(max(distances, 0));
        assert(isfinite(len));
        count = count+1;
        indices(count) = airIdx(1)+(airIdx(2)-1)*model.Nx+ ...
            (airIdx(3)-1)*model.Nx*model.Ny;
        weightedLengths(count) = weight*len;
        position = position+len*direction;
        if direction(axisID) > 0
            position(axisID) = hi(axisID);
        else
            position(axisID) = lo(axisID);
        end
        airIdx(axisID) = airIdx(axisID)+sign(direction(axisID));
    end
    indices = indices(1:count);
    weightedLengths = weightedLengths(1:count);
end
