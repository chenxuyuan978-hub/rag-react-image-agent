# Gaussian Blur Image Denoising Experiment

## Abstract

This showcase paper describes an image denoising experiment based on Gaussian
blur. The goal is to reduce light random noise from a synthetic RGB image while
preserving the main shapes and edges.

## Experiment Setting

The experiment setting uses one noisy input image and one clean reference image.
The denoising method is Gaussian blur with kernel size 5. The output image is
compared with the clean reference image after filtering.

## Metrics

The experiment reports MSE, PSNR, and SSIM. MSE should be lower for better
pixel-level reconstruction. PSNR should be higher for better signal quality.
SSIM should be closer to 1 when the restored image is structurally similar to
the clean reference image.
