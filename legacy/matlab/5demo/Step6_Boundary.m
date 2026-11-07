function [photon, event] = Step6_Boundary(photon, model, tissue, faceAxis)
    % 第6步。输入光子、模型、参数和跨越方向；输出光子及逃逸事件。
    event = struct('kind', '', 'surfaceIndex', 0, 'weight', 0, ...
        'airIndices', [], 'airWeights', []);
    nextIdx = photon.idx;
    nextIdx(faceAxis) = nextIdx(faceAxis)+sign(photon.u(faceAxis));
    outside = any(nextIdx < 1 | nextIdx > model.size);
    if outside && faceAxis==3 && photon.u(3)<0
        n1=tissue(photon.label).n; n2=tissue(1).n;
        ci=min(1,abs(photon.u(3))); st2=(n1/n2)^2*(1-ci^2);
        R=1;
        if st2<1
            ct=sqrt(1-st2);
            R=0.5*(((n1*ci-n2*ct)/(n1*ci+n2*ct))^2+ ...
                ((n1*ct-n2*ci)/(n1*ct+n2*ci))^2);
        end
        if rand<R
            photon.u(3)=-photon.u(3); return;
        end
    end
    if outside
        if faceAxis == 3 && photon.u(3) > 0
            event.kind = 'bottom';
        elseif faceAxis == 3 && photon.u(3) < 0
            event.kind = 'top';
        else
            event.kind = 'side';
        end
        event.surfaceIndex = photon.idx(1)+(photon.idx(2)-1)*model.Nx;
        event.weight = photon.weight;
        photon.alive = false;
        return;
    end
    nextLabel = double(model.T(nextIdx(1), nextIdx(2), nextIdx(3)));
    n1 = tissue(photon.label).n;
    n2 = tissue(nextLabel).n;
    reflected = false;
    if n1 ~= n2
        ci = min(1, abs(photon.u(faceAxis)));
        eta = n1/n2;
        st2 = eta^2*max(0, 1-ci^2);
        if st2 >= 1
            reflected = true;
        else
            ct = sqrt(1-st2);
            rs = ((n1*ci-n2*ct)/(n1*ci+n2*ct))^2;
            rp = ((n1*ct-n2*ci)/(n1*ct+n2*ci))^2;
            reflected = rand < (rs+rp)/2;
            if ~reflected
                tangential = [1:faceAxis-1 faceAxis+1:3];
                photon.u(tangential) = eta*photon.u(tangential);
                photon.u(faceAxis) = sign(photon.u(faceAxis))*ct;
                photon.u = photon.u/norm(photon.u);
            end
        end
    end
    if reflected
        photon.u(faceAxis) = -photon.u(faceAxis);
    else
        photon.idx = nextIdx;
    end
end
