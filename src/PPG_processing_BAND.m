ppg_data = PPG();

sample_rate = 512;

% PPG 신호 필터링
cutoff_low = 0.5; % 저역 통과 필터의 컷오프 주파수 설정
cutoff_high = 10; % 고역 통과 필터의 컷오프 주파수 설정

[b, a] = butter(2, [cutoff_low cutoff_high]/(sample_rate/2), 'bandpass');
filtered_ppg = filtfilt(b, a, ppg_data);

time = (0:length(ppg_data)-1) / sample_rate;

subplot(2,1,1);
xlim([0 length(pressure)])
plot(time, filtered_ppg);
xlabel('Time (s)');
ylabel('Filtered PPG Signal');
title('Filtered PPG Signal');

%pressure 데이터 저역 통과
pressure_data=pressure
cutoff_freq = 0.5; % 저역 통과 필터의 컷오프 주파수 설정
[b, a] = butter(2, cutoff_freq/(sample_rate/2), 'low');
filtered_pressure = filtfilt(b, a, pressure_data);
time_pressure = (0:length(pressure_data)-1) / sample_rate;



subplot(2,1,2);
xlim([0 length(pressure)])
plot(time_pressure, filtered_pressure);
xlabel('Time (s)');
ylabel('pressure (mmHg)');
title('pressure');