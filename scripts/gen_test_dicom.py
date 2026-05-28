"""生成合成CT+MRI DICOM序列用于测试"""
import numpy as np
import pydicom
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian, CTImageStorage, MRImageStorage
import os, sys

np.random.seed(42)
NUM_SLICES = 32
SIZE = 128
OUT_CT = 'test_data/ct_series'
OUT_MRI = 'test_data/mri_series'

def make_phantom(ns, sz):
    vol = np.ones((ns, sz, sz), dtype=np.int16) * (-1000)
    cx, cy = sz//2, sz//2
    for z in range(ns):
        for y in range(sz):
            for x in range(sz):
                dx = (x - cx) / (sz * 0.35)
                dy = (y - cy) / (sz * 0.45)
                dz = (z - ns//2) / (ns * 0.4)
                d = dx*dx + dy*dy + dz*dz
                if d < 1.0:
                    vol[z, y, x] = 40
                    dx2 = (x - cx) / (sz * 0.12)
                    dy2 = (y - cy) / (sz * 0.14)
                    dz2 = (z - ns//2) / (ns * 0.15)
                    if dx2*dx2 + dy2*dy2 + dz2*dz2 < 1.0:
                        vol[z, y, x] = 400
    return vol

def write_series(vol, out_dir, sop_class, modality, patient_id, pixel_repr):
    os.makedirs(out_dir, exist_ok=True)
    study_uid = pydicom.uid.generate_uid()
    series_uid = pydicom.uid.generate_uid()
    for i in range(vol.shape[0]):
        file_meta = FileMetaDataset()
        file_meta.MediaStorageSOPClassUID = sop_class
        file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
        file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
        ds = Dataset()
        ds.file_meta = file_meta
        ds.PatientName = f'Test^{modality}'
        ds.PatientID = patient_id
        ds.PatientBirthDate = '19900101'
        ds.PatientSex = 'O'
        ds.StudyInstanceUID = study_uid
        ds.SeriesInstanceUID = series_uid
        ds.StudyID = '1'
        ds.SeriesNumber = 1
        ds.SOPClassUID = sop_class
        ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
        ds.Modality = modality
        ds.SliceThickness = 1.0
        ds.SpacingBetweenSlices = 1.0
        ds.Rows, ds.Columns = vol.shape[1], vol.shape[2]
        ds.InstanceNumber = i + 1
        ds.ImagePositionPatient = [0.0, 0.0, float(i)]
        ds.ImageOrientationPatient = [1, 0, 0, 0, 1, 0]
        ds.SliceLocation = float(i)
        ds.SamplesPerPixel = 1
        ds.PhotometricInterpretation = 'MONOCHROME2'
        ds.PixelRepresentation = pixel_repr
        ds.BitsAllocated = 16
        ds.BitsStored = 16
        ds.HighBit = 15
        ds.PixelData = vol[i].tobytes()
        ds.PixelSpacing = [0.5, 0.5]
        if modality == 'CT':
            ds.RescaleIntercept = 0
            ds.RescaleSlope = 1
            ds.RescaleType = 'HU'
        ds.save_as(f'{out_dir}/{modality}_{i+1:04d}.dcm')
    return series_uid

print('Generating CT phantom...')
ct_vol = make_phantom(NUM_SLICES, SIZE)
write_series(ct_vol, OUT_CT, CTImageStorage, 'CT', 'CT001', 1)
print(f'  {NUM_SLICES} files -> {OUT_CT}/')

print('Generating MRI phantom...')
mri_vol = np.zeros((NUM_SLICES, SIZE, SIZE), dtype=np.uint16)
soft = (ct_vol > 20) & (ct_vol < 200)
bone = ct_vol >= 200
mri_vol[soft] = 180
mri_vol[bone] = 30
write_series(mri_vol, OUT_MRI, MRImageStorage, 'MR', 'MRI001', 0)
print(f'  {NUM_SLICES} files -> {OUT_MRI}/')

# Count total size
ct_size = sum(os.path.getsize(os.path.join(OUT_CT, f)) for f in os.listdir(OUT_CT))
mri_size = sum(os.path.getsize(os.path.join(OUT_MRI, f)) for f in os.listdir(OUT_MRI))
print(f'\nTotal: CT={ct_size/1024:.0f}KB, MRI={mri_size/1024:.0f}KB')
print('Done!')
