"""
DICOM加载 — pydicom + SimpleITK
"""
import os
import numpy as np
import SimpleITK as sitk
import pydicom


class DicomLoader:
    """加载DICOM序列并转换为numpy volume"""

    def load_series(self, folder_path: str) -> tuple:
        """
        加载DICOM序列
        
        Returns:
            (volume_numpy_array, metadata_dict)
            失败时返回 (None, None)
        """
        if not os.path.isdir(folder_path):
            return None, None

        try:
            # SimpleITK方式：直接读取序列
            reader = sitk.ImageSeriesReader()
            dicom_names = reader.GetGDCMSeriesFileNames(folder_path)

            if not dicom_names:
                # 递归搜索子文件夹
                dicom_names = self._find_dicom_files(folder_path)

            if not dicom_names:
                return None, None

            reader.SetFileNames(dicom_names)
            image = reader.Execute()

            # 转换为numpy
            volume = sitk.GetArrayFromImage(image)  # (Z, Y, X)
            spacing = image.GetSpacing()  # (x, y, z)
            origin = image.GetOrigin()
            direction = image.GetDirection()

            # 提取metadata
            metadata = {
                "spacing": spacing,
                "origin": origin,
                "direction": direction,
                "size": volume.shape,
                "num_slices": volume.shape[0],
                "series_description": "",
                "modality": "",
                "patient_id": "",
            }

            # 读取第一个文件的dicom tag获取更多信息
            first_dcm = pydicom.dcmread(dicom_names[0], stop_before_pixels=True)
            metadata["series_description"] = getattr(first_dcm, "SeriesDescription", "")
            metadata["modality"] = getattr(first_dcm, "Modality", "")
            metadata["patient_id"] = getattr(first_dcm, "PatientID", "")
            metadata["series_instance_uid"] = getattr(first_dcm, "SeriesInstanceUID", "")

            print(f"DICOM loaded: {volume.shape}, spacing={spacing}, modality={metadata['modality']}")
            return volume, metadata

        except Exception as e:
            print(f"DICOM加载错误: {e}")
            return None, None

    def _find_dicom_files(self, folder_path: str) -> list:
        """递归搜索DICOM文件"""
        dicom_files = []
        for root, dirs, files in os.walk(folder_path):
            for f in files:
                if f.endswith('.dcm') or f.endswith('.DCM'):
                    dicom_files.append(os.path.join(root, f))
                else:
                    # 尝试作为DICOM读取
                    try:
                        fp = os.path.join(root, f)
                        dcm = pydicom.dcmread(fp, stop_before_pixels=True)
                        if hasattr(dcm, "Modality") and hasattr(dcm, "SOPClassUID"):
                            dicom_files.append(fp)
                    except Exception:
                        pass
            if dicom_files:
                break  # 只取第一个有文件的子目录
        return sorted(dicom_files)
