%%Literature-informed TEST model; units cm^-1, wavelength nm.
% 1 air; 2 soft tissue represented by MUSCLE; 3 patella; 4 bone.
% g=.9 and n=1.4 remain explicit modeling assumptions, not measured here.
% wavelength=808;
wavelength=980;
tissue=repmat(struct('name','','mua',0,'musp',0,'mus',0, ...
    'g',0,'n',1,'basis','','assumptions',''),1,4);
names={'air','soft tissue (muscle proxy)','patella (tibia site B proxy)','bone (tibia site B proxy)'};
% mua=[0 .21 .0396 .09];
% musp=[0 7.5 (5.4+(808-785)/(830-785)*(4.4-5.4)) 6.299333333333333];
% 980 nm：髌骨暂用胫骨B点代理，并非髌骨实测值。
mua=[0 .60 .136666666666667 .136666666666667];
musp=[0 6.10 5.52 5.52];
basis={'Nonabsorbing nonscattering air', ...
 'Chaki et al 2023 Table 1 muscle at 980nm; DOI 10.1002/jbio.202200283', ...
 'Patella ASSUMED equal to tibia site B at 980nm; not measured patella; Kothuri 2025 DOI 10.1038/s41598-025-06138-y', ...
 'Kothuri 2025; Zenodo 14170681 ABC.txt site B: 980nm mean of 3 repeats: mua=(.14+.13+.14)/3; musp=(5.55+5.31+5.70)/3; DOI 10.1038/s41598-025-06138-y'};
for id=1:4
 tissue(id).name=names{id}; tissue(id).mua=mua(id); tissue(id).musp=musp(id);
 tissue(id).basis=basis{id};
 if id>1
  tissue(id).g=.9; tissue(id).n=1.4;
  tissue(id).assumptions='g=0.9; n=1.4 assumed; proxies/interpolations are not subject-specific measurements';
 end
 tissue(id).mus=tissue(id).musp/(1-tissue(id).g);
end
