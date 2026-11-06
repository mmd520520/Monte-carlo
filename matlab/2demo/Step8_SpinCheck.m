function [photon, rouletteCorrection] = Step8_SpinCheck(photon, tissue, roulette)
    % 第8步。输入光子、组织参数、轮盘赌配置；输出光子和权重修正。
    g = tissue(photon.label).g;
    if abs(g) < 1e-12
        costheta = 2*rand-1;
    elseif g >= 1
        costheta = 1;
    else
        q = (1-g^2)/(1-g+2*g*rand);
        costheta = (1+g^2-q^2)/(2*g);
    end
    costheta = min(1, max(-1, costheta));
    sintheta = sqrt(max(0, 1-costheta^2));
    psi = 2*pi*rand;
    u = photon.u;
    if abs(u(3)) < 0.9
        e1 = cross([0 0 1], u);
    else
        e1 = cross([0 1 0], u);
    end
    e1 = e1/norm(e1);
    e2 = cross(u, e1);
    photon.u = costheta*u+sintheta*(cos(psi)*e1+sin(psi)*e2);
    photon.u = photon.u/norm(photon.u);
    rouletteCorrection = 0;
    if photon.weight <= roulette.threshold
        old = photon.weight;
        if rand < roulette.chance
            photon.weight = photon.weight/roulette.chance;
        else
            photon.weight = 0;
            photon.alive = false;
        end
        rouletteCorrection = old-photon.weight;
    end
end
