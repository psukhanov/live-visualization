/*
 * ThinkGear ECG algorithm interface library.
 * Copyright (c) NeuroSky Inc. All rights reserved.
 * Siyi Deng; 05-14-2014; 07-01-2014;
 */

/**
 * @file tg_ecg.h
 * @brief ThinkGear ECG algorithm interface library. All algorithms are designed for ECG data retrieved from 
 * NeuroSky's BMD101 chip. Sampling rate is fixed at 512 Hz, ADC range is 16 bit (-32768 to +32767).
 * ECG should be taken when the user is sit calm and stable, with minimal body movement. We do not guarantee
 * the algorithm to have proper behavior if the data is taken in any situation other than above. Specifically,
 * if ECG is measured right after some heavy exercise, the algorithm output might not be reliable.
 */

#ifndef TG_ECG_H
#define TG_ECG_H

#ifdef __cplusplus
extern "C" {
#endif

#include "nsk_defines.h"

/** Get the library version string. */
int8_t*
tg_ecg_get_version(void);

/** Set to @c 1 to enable the 5-40 Hz band pass filter on raw data. */
void
tg_ecg_do_preprocessing_filter(const uint8_t x);

/** Set to @c 1 to enable the mechanical noise checker. */
void
tg_ecg_do_noise_check(const uint8_t x);

/** Set to @c 1 to enable the median smoothing filter on output HRV and HR. */
void
tg_ecg_do_median_smoothing(const uint8_t x);

/** Set to @c 1 to enable computing HRV using standard deviation method. */
void
tg_ecg_do_hrv_sdnn(const uint8_t x);

/** Set to @c 1 to enable computing the respiratory rate. */
void
tg_ecg_do_respiratory_rate(const uint8_t x);

/** Set to @c 1 to enable computing the relaxation level. */
void
tg_ecg_do_relaxation_level(const uint8_t x);

/** Set to @c 1 to enable robust HRV estimator. */
void
tg_ecg_do_hrv_robust(const uint8_t x);

/** Set to @c 1 to enable precise RR Inverval finder. */
void
tg_ecg_do_rri_precise(const uint8_t x);

/** Set to @c 1 to turn on the smoothing filter for better visualization. */
void
tg_ecg_do_smoothed_raw(const uint8_t x);

/** Set to @c 1 to turn on another (RAPS) smoothing filter for better visualization. */
void
tg_ecg_do_smoothed_raw_raps(const uint8_t x);

/** Set to @c 1 to enable computing the mood value. */
void
tg_ecg_do_mood(const uint8_t x);

/** Set to @c 1 to enable computing the stress value. */
void
tg_ecg_do_stress(const uint8_t x);

/** Set to @c 1 to enable signal quality check. */
void
tg_ecg_do_quality_check(const uint8_t x);

/**
 * Set the parameters for stress computation. Must be called before calling @c tg_ecg_init() 
 * or @c tg_ecg_reset_stress().
 * @param[in] gender  1 = female, 0 = male.
 * @param[in] age in years, 16-90.
 * @param[in] height in cm, 1-300.
 * @param[in] weight in kg, 1-300.
 * @param[in] imported_data an array of double precision floating point values, length 16,
 *            representing historical baseline values exported using @c tg_ecg_stress_export_data(),
 *            or NULL if no historical data are available.
 */
void
tg_ecg_set_stress_param(
    const int32_t gender,
    const int32_t age,
    const int32_t height,
    const int32_t weight,
    const alg_real_t* imported_data
);

/** Power line frequency in Hz, for smoothing filter. Can only take values of 50 or 60. */
void
tg_ecg_set_power_line_freq(const int32_t x);

/** Reset the signal quality checker. */
void
tg_ecg_reset_quality_check(void);

/** Reset the stress algorithm. */
void
tg_ecg_reset_stress(void);

/** Reset the ECG pipeline algorithm. */
void
tg_ecg_reset_pipe(void);

/** Reset the RAPS smoothing filter algorithm. */
void
tg_ecg_reset_smoothed_raw_raps(void);

/** Reset the smoothing filter algorithm. */
void
tg_ecg_reset_smoothed_raw(void);

/** Reset the precise RRI algorithm. */
void
tg_ecg_reset_rri_precise(void);

/** Reset the Robust HRV algorithm. */
void
tg_ecg_reset_hrv_robust(void);

/** Reset the Mood algorithm. */
void
tg_ecg_reset_mood(void);

/** Initialize the library. By default all algorithms are enabled. */
void
tg_ecg_init(void);

/**
 * Add a new raw ECG sample to the library.
 * @param[in] new_ecg_sample the new raw ECG sample to be added.
 */
void
tg_ecg_update(const int32_t new_ecg_sample);

/** Query the total number of ECG samples processed by the library since initialization. */
int32_t
tg_ecg_get_total_sample_count(void);

/** Query the total time duration passed since initialization, in units of milliseconds. */
int32_t
tg_ecg_get_total_duration(void);

/** Query the total number of RR Intervals detected since initialization. */
int32_t
tg_ecg_get_total_rri_count(void);

/**
 * Query whether the last @b processed sample is identified as the R-peak.
 * Note that the @b processed sample is delayed against the newly @b add sample by 211 samples.
 * The return value is either 1 (peak) or 0 (not-peak) */
int32_t
tg_ecg_is_r_peak(void);

/**
 * Query whether the last @b processed sample is mechanical noise.
 * Note that the @b processed sample is delayed against the newly @b add sample by 211 samples.
 * The return value is either 1 (peak) or 0 (not-peak) */
int32_t
tg_ecg_is_mechanical_noise(void);

/** Get the sample processed by pre-processing filters. It is delayed against the raw data by 211 samples. */
int32_t
tg_ecg_get_raw_filtered(void);

/** Get the sample after smoothing filters.
 *  If line noise is set to 50 Hz, the delay against the raw data is 516 samples.
 *  If line noise is set to 60 Hz, the delay against the raw data is 450 samples.
 */
alg_real_t
tg_ecg_get_raw_smoothed(void);

/** Get the sample after RAPS smoothing filters. It is delayed against the raw data by 274 samples. */
alg_real_t
tg_ecg_get_raw_smoothed_raps(void);

/**
 * Get the RRI (R-to-R Interval) in units of milliseconds.
 * If no R-peak is detected (@c tg_ecg_is_r_peak() == 0), or output is not ready, a value of -1 is returned. 
 */
int32_t
tg_ecg_get_rri(void);

/**
 * Get the current Heart Rate in units of beat-per-minute (BPM).
 * If no R-peak is detected (@c tg_ecg_is_r_peak() == 0), or output is not ready, a value of -1 is returned. 
 */
int32_t
tg_ecg_get_hr(void);

/**
 * Compute the current smoothed Heart Rate in BPM, using all available RRI values in current buffer.
 * Unlike the @c tg_ecg_get_hr function which can return -1, This function will always return
 * a HR as long as at least one RRI has been detected. It is the caller's responsibility to
 * maintain the pace and interval of calling it. For example, only call it once when
 * @c tg_ecg_is_r_peak() is true.
 */
int32_t
tg_ecg_compute_hr_now(void);

/**
 * Get the current relaxation level, in a scale of 1-100.
 * If no R-peak is detected (@c tg_ecg_is_r_peak() == 0), or output is not ready, a value of -1 is returned. 
 */
int32_t
tg_ecg_get_relaxation_level(void);

/**
 * Get the current respiratory rate, in units of breath-per-minute.
 * If no R-peak is detected (@c tg_ecg_is_r_peak() == 0), or output is not ready, a value of -1 is returned. 
 */
int32_t
tg_ecg_get_respiratory_rate(void);

/**
 * Get the current HRV computed using standard deviation, in units of milliseconds.
 * If no R-peak is detected (@c tg_ecg_is_r_peak() == 0), or output is not ready, a value of -1 is returned. 
 */
int32_t
tg_ecg_get_hrv_sdnn(void);

/**
 * Compute HRV using robust statistics based on last @c num_heart_beat RRI values. 
 * If @c num_heart_beat exceeds the amount of available RRI values in the buffer, a value of -1 is returned.
 * Note that this function is relatively expensive, therefore should only be called sparsely,
 * For example, only call it for 1 time when @c tg_ecg_is_r_peak() is true 
 * and @c tg_ecg_get_total_rri_count() is greater than @c num_heart_beat.
 * @param[in] num_heart_beat the sample size to compute HRV statistics. Suggested value: between 30 to 512.
 * @return HRV value in units of milliseconds.
 */
int32_t
tg_ecg_compute_hrv(const int32_t num_heart_beat);

/**
 * Compute HRV using robust statistics with all available RRI values in current buffer.
 * @return HRV value in units of milliseconds.
 */
int32_t
tg_ecg_compute_hrv_now(void);

/**
 * Compute Mood Value. The value will not change if no new RRI is detected.
 * We recommend to start calling this function after 14 or more RRI has been detected;
 * and update calling for each newly detected RRI, but ONLY showing results after 30th RRI has been detected,
 * and update for every 4th newly detected RRI.
 * So the calling sequence is like 14, 15, 16, 17 ...
 * and the displaying sequence is like 30, 34, 38, 42, ...
 * @return Mood value on a scale of 1-100.
 */
int32_t
tg_ecg_compute_mood_now(void);

/**
 * Get the precise RRI (R-to-R Interval) in units of milliseconds.
 * If no precise RRI is found, a value of -1 is returned.
 * This result is delayed from the preprocessed intput data by @c TG_RRI_LEN_BUFFER (31) samples
 */
int32_t
tg_ecg_get_rri_precise(void);

/**
 * Compute Heart Age, based on hrv and adjusted by real age. For best performance, the input hrv
 * should be taken from multiple sessions in different days.
 * @param[in] age, The users real age in years. Age must be no less than 16 and no more than 90;
 * @param[in] n, Length of the rest two input array. For best performance, we recommend n >= 14.
 * @param[in] hrv, An array of HRV values in ms. Should have length @c n.
 * @param[in] rr_count, An array of number of RRs that HRV was based on. Should have length @c n.
 * @return Heart Age in years. Can be 0 if there is invalid input. Valid output is between 16 to 105.
 */
int32_t
tg_ecg_compute_heart_age(
    const int32_t age,
    const int32_t n,
    const int32_t* hrv,
    const int32_t* rr_count
);

/**
 * Compute Stress value, based on current RR interval buffer and profile data and baseline data.
 * Profile and baseline must be set using @c tg_ecg_set_stress_param() before calling @c tg_ecg_init();
 * At the very first time when no historical baseline data is available, pass in an array of all zeros as baseline.
 * Each time that @c tg_ecg_compute_stress_now() is called successfully, the baseline is updated and should be
 * exported by using the @c tg_ecg_stress_export_data() function and saved externally by the API user.
 *
 * @return Stress value, in a range of 1-100. If the computation was not successful, a value of -1 is returned.
 */
int32_t
tg_ecg_compute_stress_now(void);

/**
 * Return a pointer to an array of double precision floating point values of length 16,
 * which contains the updated baseline values. This array should be saved once exported
 * and imported as historical baseline the next time stress algorithm is called for the same user.
 *
 * NOTE: The exported array should be imported the next time prior to calling @c tg_ecg_init(), and passed to
 * @c tg_ecg_set_stress_param();
 *
 */
alg_real_t*
tg_ecg_stress_export_data(void);

/**
 * Get the signal quality estimated at the current moment. The SQ ranges from 1 to 5,
 * with 5 being the best quality and 1 being the worst quality; If the algorithm has not yet settled down,
 * the SQ will be reported as -1; although this function will give SQ value for every sample update,
 * we recommend to call it at a fixed interval of 0.5 sec to 4 sec.
 */
int32_t
tg_ecg_get_signal_quality(void);

/**
 * Get the overall signal quality estimation from the beginning to the current moment.
 * The SQ ranges from 1.0 to 5.0, and 5.0 is the best quality and 1.0 the worst quality.
 * If the algorithm has not yet settled down, the SQ will be reported as -1.0;
 * This value is a weighted average of the (instantaneous) signal quality over time.
 * We recommend to call this function only when needed, for example at the end of an ECG data recording session.
 */
alg_real_t
tg_ecg_get_signal_quality_so_far(void);

#ifdef __cplusplus
}
#endif

#endif

