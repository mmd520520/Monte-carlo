%% Tissue_knee_three_tissues.m
% Approximate anatomy traced from the user's annotated reference.
% T(ix,iy,iz); cm; IDs: 1 air, 2 soft tissue, 3 patella, 4 bone.
% The OUTER contour is the knee/body boundary, NOT an extra bone layer.
% The LOWER INNER contour bounds the single bone compartment.
% Standalone geometry script: no optical coefficients or transport assumptions.
if ~exist('buildOnly','var') || ~buildOnly
 clear; clc; close all; buildOnly=false;
end
zsurf=4;
dx=.125; dy=dx; dz=dx;
Nx=160; Ny=96; Nz=168;
x=((1:Nx)-.5)*dx-10;
y=((1:Ny)-.5)*dy-6;
z=((1:Nz)-.5)*dz;
T=ones(Nx,Ny,Nz,'uint8');
[X,Z]=ndgrid(x,z);
outer=[-3 6.5;-3.6 8.5;-4 10.5;-4.8 12.1;-5 13.6;-4.6 15.2; ...
 -3.4 16.7;-1.5 18.2;.4 18.4;2.4 18.1;4.5 17;6.3 16;8 14.4; ...
 8.8 12.5;8.5 10.6;7.5 8.6;5.8 7;4.2 5.9;2.4 4.7;1 4; ...
 -.5 4;-1.8 4.8;-2.5 5.7];
bone=[-2.6 8.2;-2.9 10;-3.3 12;-3.1 13.4;-2.4 14.4;-1.4 14.6; ...
 -.7 13.9;-.1 12.3;.6 11.5;1.7 11.4;2.6 11.7;3.2 12.7;4.4 12.6; ...
 5.5 12;5.8 10.8;5.5 9.4;4.6 8.3;3.2 7.7;1.7 7.2;.4 7.8;-1 8];
curves={outer,bone};
for k=1:2
 p=curves{k}; n=size(p,1); pp=[p(end-1:end,:);p;p(1:2,:)];
 q=linspace(3,n+3,500);
 curves{k}=[interp1(1:n+4,pp(:,1),q,'pchip')', ...
            interp1(1:n+4,pp(:,2),q,'pchip')'];
end
outer=curves{1}; bone=curves{2};
a=linspace(0,2*pi,400)';
% Adult MRI: length/width about 4.4 cm, thickness about 2.0 cm.
% Meier et al., DOI: 10.1007/s00256-024-04794-1.
% Shift right/up; minimum skin clearance about .5 cm (not uniform).
patellaX=.5; patellaZ=5.8;
patella=[patellaX+2.2*cos(a),patellaZ+1*sin(a)+.2*cos(a)];
for iy=1:Ny
 section=ones(Nx,Nz,'uint8');
 s=sqrt(max(0,1-(y(iy)/4.8)^2));
 if s>0
  Xq=1+(X-1)/s; Zq=11.5+(Z-11.5)/s;
  bodyMask=inpolygon(Xq,Zq,outer(:,1),outer(:,2));
  boneMask=inpolygon(Xq,Zq,bone(:,1),bone(:,2));
  section(bodyMask)=2;
  section(bodyMask & boneMask)=4;
  sp=sqrt(max(0,1-(y(iy)/2.2)^2));
  if sp>0
   patellaMask=inpolygon(patellaX+(X-patellaX)/sp,patellaZ+(Z-patellaZ)/sp,patella(:,1),patella(:,2));
   section(bodyMask & patellaMask)=3;
  end
 end
 T(:,iy,:)=reshape(section,Nx,1,Nz);
end
if ~buildOnly
[~,iy0]=min(abs(y)); Txz=squeeze(T(:,iy0,:))';
assert(isequal(unique(T(:))',uint8(1:4)));
colors=[.97 .97 .97; .10 .75 .93; 1 .83 .05; .98 .28 .32];
fig2D=figure('Color','w','Position',[100 70 780 780]);
imagesc(x,z,Txz); axis image; hold on;
colormap(colors); caxis([.5 4.5]);
set(gca,'YDir','reverse','FontName','Microsoft YaHei','FontSize',12);
xlim([-10 10]); ylim([0 21]);
plot(outer(:,1),outer(:,2),'k','LineWidth',1.1);
plot(bone(:,1),bone(:,2),'k','LineWidth',1.1);
plot(patella(:,1),patella(:,2),'k','LineWidth',1.1);
% Outline the 2 cm collimated beam in air; the anatomy is not flattened.
plot([-1 -1 1 1],[0 4 4 0],'Color',[.72 .38 .05],'LineWidth',1.5);
for bx=[-.65 0 .65], quiver(bx,1,0,2.2,0,'Color',[.72 .38 .05],'LineWidth',1.3,'MaxHeadSize',.5); end
text(1.6,1.8,{'光柱直径 2 cm','沿 +Z 入射'},'FontName','Microsoft YaHei','FontSize',11);
plot([-7 -.1],[patellaZ patellaZ],'k-','LineWidth',1.2);
text(-9.3,patellaZ,'髌骨','FontName','Microsoft YaHei','FontWeight','bold');
plot([-6.5 -3.2],[8.4 8.4],'k-','LineWidth',1.2);
text(-9.3,8.4,'软组织','FontName','Microsoft YaHei','FontWeight','bold');
plot([-7 .8],[10 10],'k-','LineWidth',1.2);
text(-9.3,10,'骨','FontName','Microsoft YaHei','FontWeight','bold');
xlabel('x [cm]'); ylabel('深度 z [cm]');
title('按标注重建的二维组织示意图','FontName','Microsoft YaHei');
cb=colorbar; cb.Ticks=1:4;
cb.TickLabels={'空气','软组织','髌骨','骨'}; cb.FontName='Microsoft YaHei';
% NOTE: y thickness and 3-D taper are modeling assumptions, not CT/MRI data.
% This is the active four-label model used by Prepare_Inputs.
% Standalone execution opens both 2-D and 3-D anatomy views.

fig3D=Plot_Tissue3D(T,x,y,z);
end

