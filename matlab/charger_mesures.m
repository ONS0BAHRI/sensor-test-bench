function m = charger_mesures(fichier)
% CHARGER_MESURES  Lit un fichier CSV produit par le banc (dossier reports/<campagne>/raw/).
%   Colonnes : t_us, ax, ay, az (g), gx, gy, gz (deg/s), temp (degC)
%   Compatible MATLAB et GNU Octave.
  d = dlmread(fichier, ',', 1, 0);          % 1 = sauter la ligne d'en-tete
  m.t    = (d(:,1) - d(1,1)) / 1e6;          % temps en secondes
  m.ax   = d(:,2);
  m.ay   = d(:,3);
  m.az   = d(:,4);
  m.gx   = d(:,5);
  m.gy   = d(:,6);
  m.gz   = d(:,7);
  m.temp = d(:,8);
end
