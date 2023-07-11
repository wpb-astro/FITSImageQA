"""
something descriptive, perform several checks 

author: wpb-astro
date XYZ
"""

# is this needed / wanted?
from __future__ import annotations

# imports:
from astropy.io import fits
import logging
import sep

# package imports
# TODO: not sure how these should be organized...
from . import detection



# proper way to load sextractor config
# from config_sextractor import ipy

class Thing:
    def __init__(self) -> None:
        """
        # initialize the header object
        # initialize the data object
        """
        self.logger = logging.getLogger(__name__)
        # optional logger stuff: setLevel, setFormatter, handlers(?)

    def is_corrupt_or_empty(self):
        """check whether the FITS file is corrupt or empty
        """
        pass

class QAHeader(Thing):
    def __init__(self, filename_or_hdr, expected_fields=None, expected_fields_dtype=None) -> None:
        """
        hdr : can be a filename, or an hdu (result of fits.open), or fitsheader object (hdu[0].header)
        expected_fields : iterable of str
        expected_fields_dtype : iter of key-value pairs
            keys = header names (str)
            values = data types        
        """
        super().__init__()
        # parse the header, depending on what is passed
        if isinstance(filename_or_hdr, str):
            hdr = fits.getheader(filename_or_hdr)
        elif isinstance(filename_or_hdr, fits.hdu.hdulist.HDUList):
            hdr = filename_or_hdr[0].header
        else:
            hdr = filename_or_hdr
        self.hdr = hdr
        self.header_fields = set(self.hdr.keys())
        try:
            self.expected_fields = set(expected_fields)
        except TypeError:
            self.expected_fields = expected_fields
        self.expected_fields_dtype = expected_fields_dtype

    def fetch_header_info(self, column_name):
        """ 
        get info from the header

        Parameters
        ----------
        column_name : str
            should be an element of list(self.hdr.keys())
        
        Returns
        -------
        info : 
            return the value from the header, corresponding to the key `column_name`
        """
        # TODO: if the underlying exception that gets raised by astropy.io.fits is sufficient,
        #       just use that
        #       KEY QUESTION: is that exception stored to the log? if not, must do proper logging

        ### Choose scenario 1 vs 2, and uncomment/delete the appropriate one
        ### SCENARIO 1: just use the underlying exception that is raised
        info = self.hdr[column_name]
        return info

        ### SCENARIO 2: write our own handling, with logging
        #try:
        #    info = self.hdr[column_name]
        #    return info
        #except KeyError:
        #    self.logger.error("Field not found in the header.")

    def check_header_fields_present(self, expected_fields=None, 
                                    return_missing_fields=False):
        """
        parameters
        ----------
        expected_fields : iterable of str (optional)
            if passed, use instead of self.expected_fields 
        return_missing_fields : bool (default=False)
            if True, return fields from `expected_fields` that 
            are not present in image header
        
        returns
        -------
        valid : bool
            are the desired fields present in the header?
        missing_fields : iter, optional
            which fields are missing from the header (empty, if valid=True)
        """
        if expected_fields is not None:
            expected_fields = set(expected_fields)
        else:
            expected_fields = self.expected_fields
        # check whether all desired fields are present
        valid = self.header_fields.issuperset( expected_fields )
        if not return_missing_fields:
            return valid
        else:
            missing_fields = expected_fields.difference( self.header_fields )
            return valid, missing_fields
    
    def check_header_fields_dtype(self, expected_fields_dtype=None,
                                  return_incorrect_fields=False,
                                  suppress_unknown=False, verbose=False):
        """
        check that data type of header fields are as expected
        
        Parameters
        ----------
        expected_fields_dtype : iter of key-value pairs
            keys = header names (str)
            values = data types
        return_incorrect_fields : bool
            which fields are of the wrong data type (empty, if valid=True)
        suppress_unknown : bool
            if True, do not break if header datatype cannot be checked 
            (not in reference list)
        verbose : bool
            print warnings if fields cannot be checked, or if fields are wrong data type
        
        Returns
        -------
        valid : bool
            are the header fields of the expected data type?
        """
        pass

class QAData(Thing):
    def __init__(self, filename_or_data, detection_config=None) -> None:
        """
        Parameters
        ----------
        filename_or_data : str | HDUList | np.ndarray
            can be a filename, or an hdu (result of fits.open), or fitsheader object (hdu[0].header)
        detection_config : dict (optional)
            dictionary of parameters to use in `detection.extract_sources`
        """
        super().__init__()
        # parse the data, depending on what is passed
        if isinstance(filename_or_data, str):
            data = fits.getdata(filename_or_data)
        elif isinstance(filename_or_data, fits.hdu.hdulist.HDUList):
            data = filename_or_data[0].data
        else:
            data = filename_or_data
        self.data = data
        self.detection_config = detection_config

    def is_focus_good(self, max_focus_fwhm=2.5): #or, rename as check_focus
        """
        Determine whether a focus run is needed while observing,
        by comparing the FWHM of sources that are detected in the image
        to a user-specified maximum threshold
        
        Parameters
        ----------
        max_focus_fwhm : float
            maximum value of the FWHM, to consider the image to be in focus
        
        Returns
        -------
        in_focus : bool
            True, if med_fwhm <= max_focus_fwhm
        med_fwhm : float
            median FWHM of detected sources
            
        Notes
        -----
        source detection will be run via self.detect_sources
            if no result already exists (stored in self.sources)
        """
        try:
            _ = self.sources
        except AttributeError:
            self.detect_sources()

        # TODO: confirm that this median method is robust against nan/missing
        med_fwhm = np.median( self.sources.cat['fwhm'] )
        in_focus = med_fwhm <= max_focus_fwhm
        return in_focus, med_fwhm

    def detect_sources(self, detection_config=None, overwrite=True, **kwargs):
        """ 
        Detect sources in the image and store the result as an attribute

        Parameters
        ----------
        detection_config : dict
            dictionary of source detection parameters that will be
            passed to detection.extract_sources
        overwrite : bool
            if True, will automatically overwrite existing `sources`
        kwargs : additional arguments to pass to detection.extract_sources 

        Returns
        -------
        None
            set (or overwrite) self.sources with an instance of the detection.Sources class

        Notes
        -----
        If `sources` attribute already exists, it will be overwritten
        """
        # should the image header be updated, e.g., with number of sources detected???
        #   --> A: probably not here, but maybe elsewhere
        try:
            _ = self.sources 
            if not overwrite:
                raise Exception("Aborting: self.sources already exists. Must set overwrite=True to proceed.")
            logger.info("Overwriting self.sources with new result.")
        except AttributeError:
            logger.info("Sources have not yet been extracted. The new result will be stored in self.sources")
        
        # collect the locally-passed source detection parameters
        if detection_config is None:
            detection_config = kwargs
        else:
            detection_config.update(kwargs)
        
        # update the class attribute
        if self.detection_config is not None:
            self.detection_config.update(detection_config)
        else:
            self.detection_config = detection_config
        
        # TODO: NOT YET IMPLEMENTED: Attempt to parse the zeropoint from the header (used for calculating magnitudes.)
        #       loop through a list of possible zeropoint keywords 
        # list of possible zeropoint keywords in the header
        zp_keyword_list = ['ZP', 'ZPMAG'] 
        zp = None
        #while zp is None:
        #    try:
        #        zp = # read the value from the header
        detection_config['zp'] = zp

        # run the source detection and store the result
        self.sources = detection.extract_sources(path_or_pixels=self.data, logger=self.logger, **self.detection_config)
    