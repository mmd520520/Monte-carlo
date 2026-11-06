function outputFiles = Step10_Plot(results, outputFile, visible)
    % Monte Carlo tissue fluence plus analytic incident fluence in air.
    if nargin < 2
        outputFile = fullfile(fileparts(mfilename('fullpath')), 'fluence_section.png');
    end
    if nargin < 3
        visible = true;
    end
    if visible
        visibility = 'on';
    else
        visibility = 'off';
    end
    outputFiles = {outputFile};
    results = AddIncidentAirBeam(results);
    iy = round(size(results.Phi, 2)/2);
    section = squeeze(results.Phi(:, iy, :))';
    section(section <= 0) = NaN;
    fig = figure('Color', 'w', 'Visible', visibility, 'Position', [100 100 850 740]);
    im = imagesc(results.x, results.z, log10(section));
    set(im, 'AlphaData', isfinite(section));
    set(gca, 'YDir', 'reverse', 'Color', [0.93 0.93 0.93], 'FontSize', 12);
    axis image;
    xlim([-1.5 1.5]);
    ylim([0 3]);
    clim([-4 0.5]);
    colormap(jet(256));
    cb = colorbar;
    cb.Label.String = 'log_{10}(fluence [mm^{-2}])';
    xlabel('x [mm]');
    ylabel('z [mm]');
    hold on;
    theta = linspace(0, 2*pi, 300);
    plot(0.5*cos(theta), 2+0.5*sin(theta), 'k--', 'LineWidth', 1.3);
    yline(1, 'k:');
    yline(1.1, 'k:');
    title(sprintf('500 nm, 1 mm beam | N = %g | grid = %d x %d x %d', ...
        results.Nphotons, size(results.Phi, 1), size(results.Phi, 2), size(results.Phi, 3)));
    if isfield(results, 'airDiffusePhi')
        airCaption = 'Air: incident + specular + Monte Carlo escaping rays';
    else
        airCaption = 'Air: incident + specular only; diffuse rays unavailable';
    end
    subtitle(airCaption);
    exportgraphics(fig, outputFile, 'Resolution', 180);
    if ~visible
        close(fig);
    end

    % A separate, explicitly labeled binned view improves low-count readability.
    % Average a 0.2 mm slab around y=0, then average 0.1 x 0.1 mm x-z bins.
    if size(results.Phi, 1) == 400 && size(results.Phi, 3) == 400
        slab = mean(results.Phi(:, 191:210, :), 2);
        slab = squeeze(slab);
        binned = squeeze(mean(mean(reshape(slab, 10, 40, 10, 40), 1), 3))';
        binned(binned <= 0) = NaN;
        fig = figure('Color', 'w', 'Visible', visibility, 'Position', [100 100 850 740]);
        im = imagesc(-1.95:0.1:1.95, 0.05:0.1:3.95, log10(binned));
        set(im, 'AlphaData', isfinite(binned));
        set(gca, 'YDir', 'reverse', 'Color', [0.93 0.93 0.93], 'FontSize', 12);
        axis image;
        xlim([-1.5 1.5]);
        ylim([0 3]);
        clim([-4 0.5]);
        colormap(jet(256));
        cb = colorbar;
        cb.Label.String = 'log_{10}(mean fluence [mm^{-2}])';
        xlabel('x [mm]');
        ylabel('z [mm]');
        hold on;
        plot(0.5*cos(theta), 2+0.5*sin(theta), 'k--', 'LineWidth', 1.3);
        yline(1, 'k:');
        yline(1.1, 'k:');
        title(sprintf('500 nm | N = %g | original simulation grid: 400^3', results.Nphotons));
        subtitle({airCaption, ...
            'Display: 0.2 mm y slab, 0.1 mm x-z bins; gray = zero/unsampled'});
        [folder, stem, ext] = fileparts(outputFile);
        binnedFile = fullfile(folder, [stem '_binned' ext]);
        exportgraphics(fig, binnedFile, 'Resolution', 180);
        outputFiles{end+1} = binnedFile;
        if ~visible
            close(fig);
        end
    end
end
