# imports
from FITSImageQA.imageqa import QAHeader, QAData


def assertHeaderNotEmpty(self):
    """
    Confirms that the returned header object is not empty.

    Header from astropy.io.
    """
    qa_header = QAHeader("../FITSImageQA_example_images/hlsp_hlf_hst_wfc3-60mas_goodss_f140w_v2.0_sci_cutout_1arcmin.fits")
    self.assertTrue(qa_header)


def assertDataNotEmpty(self):
    """
    Confirms that the returned data object is not empty.

    Data from astropy.io.
    """
    qa_data = QAData('../FITSImageQA_example_images/hlsp_hlf_hst_wfc3-60mas_goodss_f140w_v2.0_sci_cutout_1arcmin.fits')
    self.assertTrue(qa_data)
