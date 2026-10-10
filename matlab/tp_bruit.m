% TP T03 - Bruit au repos, refait en MATLAB a partir des donnees du banc.
% Resultat attendu : les memes valeurs que le rapport Python (ecart-type, SNR).

campagne = 'METTRE_ICI_LE_NOM_DE_LA_CAMPAGNE';   % ex. 20261010-122946_sil_SIM-0001
dossier  = fullfile('..', 'reports', campagne, 'raw');
fs = 500;                                          % frequence d'echantillonnage (Hz)

m = charger_mesures(fullfile(dossier, 'T03_repos.csv'));

ecarts_mg = [std(m.ax) std(m.ay) std(m.az)] * 1000;
fprintf('Ecart-type ax, ay, az : %.2f  %.2f  %.2f mg\n', ecarts_mg);
fprintf('SNR pour 1 g : %.1f dB\n', 20 * log10(1 / (max(ecarts_mg) / 1000)));

% Spectre d'amplitude avec fenetre de Hann (meme calcul que processing/signal_tools.py)
x = m.az - mean(m.az);
n = numel(x);
w = 0.5 - 0.5 * cos(2 * pi * (0:n-1)' / (n - 1));
X = abs(fft(x .* w)) * 2 / sum(w);
f = (0:n-1)' * fs / n;
moitie = 2:floor(n / 2);                           % frequences positives, sans le continu

figure('Name', 'T03 - Bruit au repos');
subplot(1, 2, 1);
hist(x * 1000, 50);
xlabel('bruit sur Z (mg)'); ylabel('nombre'); title('Distribution du bruit');
subplot(1, 2, 2);
semilogy(f(moitie), X(moitie) * 1000);
xlabel('frequence (Hz)'); ylabel('amplitude (mg)'); title('Spectre du bruit');
grid on;
