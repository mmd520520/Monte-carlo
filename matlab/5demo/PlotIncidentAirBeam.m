function displayPhi = PlotIncidentAirBeam(results)
% DISPLAY ONLY: replace upper-air MC samples by the prescribed incident field.
% No MC return light is included in this displayed air region.
% Tissue voxels and the saved MC results remain unchanged.
%仅用于绘图：生成空气中只显示规定入射光柱的示意场，隐藏返回光，不改仿真结果。
displayPhi=results.fluenceWcm2;
s=results.source;
u=[s.ux s.uy s.uz];
if isfield(s,'uAir'), u=s.uAir; end
assert(u(3)>0,'Beam must point toward increasing depth.');
xc=results.x(:); yc=results.y(:)';
E=s.power/(pi*s.radius^2); % W/cm^2 of the surface footprint
for iz=find(results.z<s.z)
    t=(s.z-results.z(iz))/u(3);
    atSurfaceX=xc+t*u(1);
    atSurfaceY=yc+t*u(2);
    disk=(atSurfaceX-s.x).^2+(atSurfaceY-s.y).^2<=s.radius^2;
    air=results.tissueLabels(:,:,iz)==1;
    layer=displayPhi(:,:,iz);
    layer(air)=0;
    layer(air & disk)=E/u(3);
    displayPhi(:,:,iz)=layer;
end
end
