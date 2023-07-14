"""
something descriptive, perform several checks 

author: wpb-astro
date XYZ
"""

# is this needed / wanted?
from __future__ import annotations

# imports:
import numpy as np
from astropy.io import fits
import logging
import matplotlib.pyplot as plt

# package imports
# TODO: not sure how these should be organized...
try:
    from . import detection
except ImportError:
    logging.critical('Unable to import detection submodule!')



# proper way to load sextractor config
# from config_sextractor import ipy

all = []

class Thing:
    def __init__(self) -> None:
        """

        TODO:
            # initialize the header object
            # initialize the data object
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        # optional logger stuff: setLevel, setFormatter, handlers(?)

    def is_corrupt_or_empty(self):
        """
        check whether the FITS file is corrupt or empty

        TODO: fill in
        """
        pass

class QAHeader(Thing):
    def __init__(self, filename_or_hdr: str | fits.hdu.hdulist.HDUList | fits.header.Header, 
                 expected_fields: list[str] = None, 
                 expected_fields_dtype: dict = None
                ) -> None:
        """

        Parameters
        ----------
        filename_or_hdr : str | astropy.io.fits.hdu.hdulist.HDUList | astropy.io.fits.header.Header
            used for creating the main header object
            can be a filename, or an hdu (result of fits.open), or fitsheader object (hdu[0].header)
        expected_fields : iterable of str (optional)
            list of fields that must appear in the image header
        expected_fields_dtype : dict of key-value pairs (optional)
            keys = header names (str)
            values = data types        
        """
        super().__init__()
        # parse the header, depending on what is passed
        if isinstance(filename_or_hdr, str):
            hdr = fits.getheader(filename_or_hdr)
        elif isinstance(filename_or_hdr, fits.hdu.hdulist.HDUList):
            hdr = filename_or_hdr[0].header
        elif isinstance(filename_or_hdr, fits.header.Header):
            hdr = filename_or_hdr
        else:
            raise TypeError("filename_or_hdr is not the correct type.")
        self.hdr = hdr
        self.header_fields = set(self.hdr.keys())
        try:
            self.expected_fields = set(expected_fields)
        except TypeError:
            self.expected_fields = expected_fields
        self.expected_fields_dtype = expected_fields_dtype

    def fetch_header_info(self, column_name: str, suppress_error: bool = False):
        """ 
        Get info from the header

        Parameters
        ----------
        column_name : str
            should be an element of list(self.hdr.keys())
        suppress_error : bool
            fail silently, if the value is not found
        
        Returns
        -------
        info : 
            return the value from the header, corresponding to the key `column_name`
        """
        try:
            info = self.hdr[column_name]
            return info
        except KeyError as e:
            if not suppress_error:
                self.logger.error("Available header fields: %s", self.header_fields)
                raise e

    def check_header_fields_present(self, expected_fields: list[str] = None, 
                                    return_missing_fields: bool = False,
                                    overwrite_attribute: bool = False):
        """

        Parameters
        ----------
        expected_fields : iterable of str (optional)
            if passed, use instead of self.expected_fields 
        return_missing_fields : bool (default=False)
            if True, return fields from `expected_fields` that 
            are not present in image header
        overwrite_attribute : bool (default=False)
            reset the `expected_fields` attribute with the locally-passed list
        
        Returns
        -------
        valid : bool
            are the desired fields present in the header?
        missing_fields : iter, optional
            which fields are missing from the header (empty, if valid=True)
        """
        if expected_fields is not None:
            expected_fields = set(expected_fields)
            if overwrite_attribute:
                self.expected_fields = expected_fields
        else:
            expected_fields = self.expected_fields
        
        # check whether all desired fields are present
        valid = self.header_fields.issuperset( expected_fields )
        if not return_missing_fields:
            return valid
        else:
            missing_fields = expected_fields.difference( self.header_fields )
            return valid, missing_fields
    
    def check_header_fields_dtype(self, expected_fields_dtype: dict = None,
                                  return_incorrect_fields: bool = False,
                                  exit_on_fail: bool = True,
                                  suppress_unknown: bool = True, 
                                  overwrite_attribute: bool = False,
                                  verbose: bool = False):
        """
        Check that data type of header fields are as expected
        
        Parameters
        ----------
        expected_fields_dtype : iter of key-value pairs
            keys = header names (str)
            values = data types (result of `type()` or iter of result of `type()`)
        return_incorrect_fields : bool
            which fields are of the wrong data type (empty, if valid=True)
        exit_on_fail : bool
            raise TypeError at first instance of failure
        suppress_unknown : bool
            if True, do not break if header datatype cannot be checked 
            (not in reference list)
        overwrite_attribute : bool (default=False)
            reset the `expected_fields_dtype` attribute with the locally-passed list
        verbose : bool
            print warnings if fields cannot be checked, or if fields are wrong data type
        
        Returns
        -------
        passed : bool
            are the header fields of the expected data type?
        incorrect_fields : dict (optional)
            keys : str, column names that did not pass the dtype check
            values : list of str [header_value, type(header_value)]

        Notes
        -----
        self.header_fields and keys(expected_fields_dtype) can be overlapping or subsets of one another
        """
        # Force behavior
        if return_incorrect_fields == exit_on_fail == True:
            raise Exception("Cannot set both `return_incorrect_fields` and `exit_on_fail` to be True")
        
        # Identify the set of fields to be checked, and optionally store it as an attribute
        if expected_fields_dtype is not None:
            if overwrite_attribute:
                self.expected_fields_dtype = expected_fields_dtype
        else:
            expected_fields_dtype = self.expected_fields_dtype

        if not isinstance(expected_fields_dtype, dict):
            raise TypeError("`expected_fields_dtype` should be a dictionary.") 

        # raise warning if no values can be checked:
        if not len( set(expected_fields_dtype.keys()).intersection( set(self.header_fields)) ):
            self.logger.warning("No overlap between header keys and fields that are requested to be checked.")

        failed_fields = dict()
        # loop through the fields that are requesting to be checked:
        for k,v in expected_fields_dtype.items():
            if k not in self.header_fields:
                if verbose:
                    self.logger.info(f"Field {k} is not in the header.")
                continue
            hdr_value = self.fetch_header_info(k) #, suppress_error=True)
            try:
                len(v)
            except TypeError:
                v = [v]
            # iterate through possible acceptable types:
            for vi in v:
                if vi == float: # more general float check
                    passed = np.issubdtype( type(hdr_value) , np.floating )
                elif vi == int: # more general int check
                    passed = np.issubdtype( type(hdr_value) , np.integer )
                else:
                    passed = isinstance( hdr_value, vi)
                if passed:
                    break
            if not passed:
                if exit_on_fail:
                    # Weird issue where the type(hdr_value) does not appear in the TypeError
                    #   --> Hack: explicitly log the message 
                    msg = "Field {k} = {val} has incorrect dtype ({dt})".format(k=k, val=hdr_value, dt=type(hdr_value))
                    self.logger.error(msg) 
                    raise TypeError(msg) 
                else:
                    failed_fields[k] = [hdr_value, type(hdr_value)]

        if exit_on_fail: 
            return passed 
        else:
            passed = len(failed_fields) == 0
            if return_incorrect_fields:
                return passed, failed_fields
            else:
                return passed 

class QAData(Thing):
    def __init__(self, filename_or_data: str | fits.hdu.hdulist.HDUList | np.ndarray, 
                 detection_config: dict = None
                ) -> None:
        """

        Parameters
        ----------
        filename_or_data : str | HDUList | np.ndarray
            used for creating the main data object
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
        elif isinstance(filename_or_data, np.ndarray):
            data = filename_or_data
        else:
            raise TypeError("filename_or_data is not the correct type.")
        self.data = data
        self.detection_config = detection_config

    def is_focus_good(self, max_focus_fwhm: float | int = 2.5): 
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
        Source detection will be run via self.detect_sources
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

    def detect_sources(self, detection_config: dict = None, 
                       overwrite: bool = True, **kwargs):
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
            self.logger.info("Overwriting self.sources with new result.")
        except AttributeError:
            self.logger.info("Sources have not yet been extracted. The new result will be stored in self.sources")
        
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
        zp_keyword_list = ['ZP', 'ZPMAG', 'ZEROPNT'] 
        zp = None
        #while zp is None:
        #    try:
        #        zp = # read the value from the header
        detection_config['zp'] = zp

        # run the source detection and store the result
        self.sources = detection.extract_sources(path_or_pixels=self.data, logger=self.logger, **self.detection_config)
    
    def display_image(self, add_detections: bool = False, **kwargs):
        """ 
        Display the image

        Parameters
        ----------
        add_detections : (bool)
            overplot sources detected via the `detect_sources` method
        kwargs (optional)
            passed to <INSERT_PLOTTING_FUNCTION>

        Returns
        -------
        fig : <INSERT_PLOTTING_FUNCTION> 

        """
        if add_detections:
            try:
                _ = self.sources 
                raise NotImplementedError("Overplotting source detection functionality has been added yet") 
            except AttributeError:
                self.logger.warning("Sources have not yet been extracted. " +\
                                    "Automatically calling `detect_sources` with default parameters, prior to plotting.")
                self.detect_sources()

        fig = plt.figure()
        plt.imshow(self.data, **kwargs)
            
        return fig

    