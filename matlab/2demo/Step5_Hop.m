function [photon, deposits, event, boundaryCount] = Step5_Hop(photon, model, tissue)
    % 第5步。输入：光子状态、组织模型、光学参数。
    % 输出：更新的光子、本次各段沉积、逃逸事件、跨界次数。
    % 大型累计数组由主程序维护，避免在逐段函数中反复复制。
    tau = -log(max(rand, realmin));
    reachedScatter = false;
    boundaryCount = 0;
    deposits = struct('indices', zeros(32, 1), 'weights', zeros(32, 1));
    count = 0;
    event = struct('kind', '', 'surfaceIndex', 0, 'weight', 0, 'airIndices', [], 'airWeights', []);
    while photon.alive && ~reachedScatter
        photon.label = double(model.T(photon.idx(1), photon.idx(2), photon.idx(3)));
        mua = tissue(photon.label).mua;
        mus = tissue(photon.label).mus;
        lo = (photon.idx-1).*model.spacing-model.offset;
        hi = photon.idx.*model.spacing-model.offset;
        distances = inf(1, 3);
        pos = photon.u > 0;
        neg = photon.u < 0;
        distances(pos) = (hi(pos)-photon.p(pos))./photon.u(pos);
        distances(neg) = (lo(neg)-photon.p(neg))./photon.u(neg);
        assert(all(distances >= -1e-8), '光子偏离当前体素。');
        [boundaryDistance, faceAxis] = min(max(distances, 0));
        if mus > 0
            scatterDistance = tau/mus;
        else
            scatterDistance = inf;
        end
        hitBoundary = boundaryDistance <= scatterDistance;
        len = min(boundaryDistance, scatterDistance);
        assert(isfinite(len));
        [photon.weight, absorbed] = Step7_Drop(photon.weight, mua, len);
        count = count+1;
        deposits.indices(count) = photon.idx(1)+(photon.idx(2)-1)*model.Nx+ ...
            (photon.idx(3)-1)*model.Nx*model.Ny;
        deposits.weights(count) = absorbed;
        photon.p = photon.p+len*photon.u;
        tau = max(0, tau-mus*len);
        if hitBoundary
            if photon.u(faceAxis) > 0
                photon.p(faceAxis) = hi(faceAxis);
            else
                photon.p(faceAxis) = lo(faceAxis);
            end
            [photon, event] = Step6_Boundary(photon, model, tissue, faceAxis);
            boundaryCount = boundaryCount+1;
        else
            reachedScatter = true;
        end
    end
    deposits.indices = deposits.indices(1:count);
    deposits.weights = deposits.weights(1:count);
end
