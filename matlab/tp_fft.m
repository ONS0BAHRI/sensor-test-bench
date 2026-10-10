% TP T07 - Retrouver la frequence de modulation du vibreur par FFT de l'enveloppe.
% Ici l'enveloppe est faite avec une moyenne glissante (fonctions de base uniquement).
% Exercice : avec la Signal Processing Toolbox, remplacez-la par butter + filtfilt
% (ordre 4, coupure 60 Hz) comme dans le code Python, et comparez.

campagne  = 'METTRE_ICI_LE_NOM_DE_LA_CAMPAGNE';
dossier   = fullfile('..', 'reports', campagne, 'raw');
fs        = 500;
f_commande = 10;                                   % fichiers disponibles : 5, 10, 20, 40 Hz

m = charger_mesures(fullfile(dossier, sprintf('T07_vibration_%dHz.csv', f_commande)));

redresse = abs(m.az - mean(m.az));                 % redressement
k = 9;                                             % moyenne sur 9 points = coupure vers 55 Hz
enveloppe = conv(redresse, ones(k, 1) / k, 'same');

x = enveloppe - mean(enveloppe);
n = numel(x);
w = 0.5 - 0.5 * cos(2 * pi * (0:n-1)' / (n - 1));
X = abs(fft(x .* w)) * 2 / sum(w);
f = (0:n-1)' * fs / n;
bande = find(f >= 1 & f <= 60);
[~, i] = max(X(bande));
f_mesuree = f(bande(i));
fprintf('Frequence commandee %d Hz, frequence mesuree %.2f Hz\n', f_commande, f_mesuree);

figure('Name', 'T07 - FFT de l''enveloppe');
subplot(2, 1, 1);
sel = m.t < 0.5;
plot(m.t(sel), m.az(sel), m.t(sel), enveloppe(sel) + mean(m.az));
xlabel('temps (s)'); ylabel('g'); legend('brut', 'enveloppe'); grid on;
subplot(2, 1, 2);
plot(f(bande), X(bande) * 1000);
xlabel('frequence (Hz)'); ylabel('amplitude (mg)');
title(sprintf('Pic a %.2f Hz', f_mesuree)); grid on;
