% TP T04 - Linearite : regression de la mesure sur g*sin(angle).
% Resultat attendu : meme gain, offset et R2 que le rapport Python.

campagne = 'METTRE_ICI_LE_NOM_DE_LA_CAMPAGNE';
dossier  = fullfile('..', 'reports', campagne, 'raw');
pleine_echelle = 2;                                % g

fichiers = dir(fullfile(dossier, 'T04_angle_*.csv'));
angles  = zeros(numel(fichiers), 1);
mesures = zeros(numel(fichiers), 1);
for i = 1:numel(fichiers)
  nom = fichiers(i).name;                          % ex. T04_angle_+30.csv
  angles(i) = str2double(nom(11:end-4));           % '+30' -> 30
  m = charger_mesures(fullfile(dossier, nom));
  mesures(i) = mean(m.ax);
end
[angles, ordre] = sort(angles);
mesures = mesures(ordre);

attendu = sind(angles);                            % en g
p = polyfit(attendu, mesures, 1);                  % p(1) = gain, p(2) = offset
ajuste  = polyval(p, attendu);
residus = mesures - ajuste;
r2 = 1 - sum(residus .^ 2) / sum((mesures - mean(mesures)) .^ 2);
erreur_pe = max(abs(residus)) / pleine_echelle * 100;

fprintf('Gain %.4f   offset %.4f g   R2 %.5f   erreur max %.3f %% PE\n', p(1), p(2), r2, erreur_pe);

figure('Name', 'T04 - Linearite');
subplot(1, 2, 1);
plot(attendu, mesures, 'o', attendu, ajuste, '-');
xlabel('attendu g*sin(theta) (g)'); ylabel('mesure (g)');
title(sprintf('R2 = %.5f', r2)); legend('mesures', 'droite ajustee', 'Location', 'northwest');
grid on;
subplot(1, 2, 2);
bar(angles, residus * 1000);
xlabel('angle (deg)'); ylabel('ecart a la droite (mg)'); title('Erreur de linearite');
grid on;
