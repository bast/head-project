import os


if "TMS_DEBUG" in os.environ:
    print("TMS_DEBUG is set")
else:
    from simnibs import mni2subject_coords


def convert_mni_to_subject(x, y, z, m2m_path):
    if "TMS_DEBUG" in os.environ:
        return float(x), float(y), float(z)
    else:
        return mni2subject_coords([x, y, z], m2m_path)
