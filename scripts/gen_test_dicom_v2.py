"""生成合成CT+MRI DICOM序列用于测试 — v2: 带完整DICOM头部"""
import numpy as np
import pydicom
from pydicom.dataset import Dataset, FileMetaDataset, FileDataset
from pydicom.uid import ExplicitVRLittleEndian, CTImageStorage, MRImageStorage
import os

NUM_SLICES = 64
SIZE = 192
OUT_CT = 'test_data/ct_series_v2'
OUT_MRI = 'test_data/mri_series_v2'


def make_phantom(ns, sz):
    vol = np.ones((ns, sz, sz), dtype=np.int16) * (-1000)
    cx, cy = sz//2, sz//2
    for z in range(ns):
        for y in range(sz):
            for x in range(sz):
                dx = (x - cx) / (sz * 0.35)
                dy = (y - cy) / (sz * 0.45)
                dz = (z - ns//2) / (ns * 0.4)
                if dx*dx + dy*dy + dz*dz < 1.0:
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
        # 必须先生成SOP Instance UID再设置FileMeta
        sop_uid = pydicom.uid.generate_uid()

        file_meta = FileMetaDataset()
        file_meta.MediaStorageSOPClassUID = sop_class
        file_meta.MediaStorageSOPInstanceUID = sop_uid
        file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
        file_meta.ImplementationClassUID = pydicom.uid.generate_uid()

        ds = FileDataset(
            f'{out_dir}/{modality}_{i+1:04d}.dcm',
            {},
            file_meta=file_meta,
            preamble=b'\x00' * 128
        )

        ds.PatientName = f'Test^{modality}'
        ds.PatientID = patient_id
        ds.PatientBirthDate = '19900101'
        ds.PatientSex = 'O'
        ds.StudyInstanceUID = study_uid
        ds.SeriesInstanceUID = series_uid
        ds.StudyID = '1'
        ds.SeriesNumber = 1
        ds.SOPClassUID = sop_class
        ds.SOPInstanceUID = sop_uid
        ds.Modality = modality
        ds.SliceThickness = 1.0
        ds.SpacingBetweenSlices = 1.0
        ds.Rows = vol.shape[1]
        ds.Columns = vol.shape[2]
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


print('Generating CT phantom (192x192, 64 slices)...')
ct_vol = make_phantom(NUM_SLICES, SIZE)
write_series(ct_vol, OUT_CT, CTImageStorage, 'CT', 'CT001', 1)
ct_size = sum(os.path.getsize(os.path.join(OUT_CT, f)) for f in os.listdir(OUT_CT))
print(f'  {NUM_SLICES} files -> {OUT_CT}/ ({ct_size/1024:.0f}KB)')

print('Generating MRI phantom...')
mri_vol = np.zeros((NUM_SLICES, SIZE, SIZE), dtype=np.uint16)
soft = (ct_vol > 20) & (ct_vol < 200)
bone = ct_vol >= 200
mri_vol[soft] = 180
mri_vol[bone] = 30
write_series(mri_vol, OUT_MRI, MRImageStorage, 'MR', 'MRI001', 0)
mri_size = sum(os.path.getsize(os.path.join(OUT_MRI, f)) for f in os.listdir(OUT_MRI))
print(f'  {NUM_SLICES} files -> {OUT_MRI}/ ({mri_size/1024:.0f}KB)')

# Verify with pydicom
dcm = pydicom.dcmread(f'{OUT_CT}/CT_0001.dcm')
print(f'\nVerify CT: {dcm.Modality}, {dcm.Rows}x{dcm.Columns}, '
      f'preamble={dcm.preamble[:4]}')
print(f'\nDone! Total: {(ct_size+mri_size)/1024:.0f}KB')
