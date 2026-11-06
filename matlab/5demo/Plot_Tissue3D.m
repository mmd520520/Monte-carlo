function fig = Plot_Tissue3D(inputModel,x,y,z)
% Show surfaces extracted from the 3-D tissue voxel labels.
% Usage:
%   Plot_Tissue3D(results)   % saved simulation result with tissueLabels,x,y,z
%   Plot_Tissue3D(T,x,y,z)   % T(ix,iy,iz) from Tissue_knee.m
% IDs: 1 air, 2 soft tissue, 3 patella, 4 bone. Length unit: cm.
%绘制三维组织模型：外轮廓、髌骨和下方骨。
source=[];
if isstruct(inputModel)
    if isfield(inputModel,'tissueLabels')
        T=inputModel.tissueLabels;
    elseif isfield(inputModel,'T')
        T=inputModel.T;
    else
        error('Input struct must contain tissueLabels or T.');
    end
    x=inputModel.x; y=inputModel.y; z=inputModel.z;
    if isfield(inputModel,'source'), source=inputModel.source; end
else
    assert(nargin==4,'Use Plot_Tissue3D(T,x,y,z) or Plot_Tissue3D(results).');
    T=inputModel;
end
assert(isequal(size(T),[numel(x),numel(y),numel(z)]),'Array axes do not match.');
fig=figure('Color','w','Name','3D voxel tissue model','Position',[120 80 880 730]);
ax=axes(fig); hold(ax,'on');
colors=[.10 .75 .93;1 .83 .05;.98 .28 .32];
handles=gobjects(1,3);
for k=1:3
    if k==1
        mask=T>1; % translucent exterior enclosing all knee tissues
        alpha=.16;
    elseif k==2
        mask=T==3; alpha=1;
    else
        mask=T==4; alpha=.95;
    end
    % isosurface uses rows=y and columns=x, unlike T(ix,iy,iz).
    % Pad with air, so surfaces remain closed at grid edges.
    V=permute(single(mask),[2 1 3]);
    padded=zeros(size(V)+2,'single');
    padded(2:end-1,2:end-1,2:end-1)=V;
    xp=[x(1)-(x(2)-x(1)), x(:)', x(end)+(x(2)-x(1))];
    yp=[y(1)-(y(2)-y(1)), y(:)', y(end)+(y(2)-y(1))];
    zp=[z(1)-(z(2)-z(1)), z(:)', z(end)+(z(2)-z(1))];
    surface=isosurface(xp,yp,zp,padded,.5);
    handles(k)=patch(ax,surface,'FaceColor',colors(k,:), ...
        'EdgeColor','none','FaceAlpha',alpha);
end
% Beam position follows the source settings saved with the result.
if isempty(source)
    source=struct('x',0,'y',0,'radius',1,'z',4,'emissionZ',0);
end
if ~isfield(source,'emissionZ'), source.emissionZ=0; end
[bx,by,bz]=cylinder(source.radius,64);
surf(ax,source.x+bx,source.y+by, ...
    source.emissionZ+(source.z-source.emissionZ)*bz, ...
    'FaceColor',[.85 .45 .08],'FaceAlpha',.28,'EdgeColor','none', ...
    'HandleVisibility','off');
set(ax,'ZDir','reverse','FontName','Microsoft YaHei','FontSize',11);
axis(ax,'equal'); axis(ax,'tight'); grid(ax,'on'); box(ax,'on');
xlabel(ax,'x [cm]'); ylabel(ax,'y [cm]'); zlabel(ax,'深度 z [cm]');
title(ax,{'三维体素组织模型','透明青色为外轮廓  黄色为髌骨  红色为骨'}, ...
    'FontName','Microsoft YaHei');
legend(ax,handles,{'软组织外轮廓','髌骨','骨'}, ...
    'Location','northeastoutside','FontName','Microsoft YaHei');
view(ax,35,22); axes(ax); camlight('headlight'); lighting gouraud;
rotate3d(fig,'on');
% Actual MC data are the labels in T; this display extracts their surfaces.
% It does not recover patient-specific 3-D anatomy from the original 2-D image.
end

