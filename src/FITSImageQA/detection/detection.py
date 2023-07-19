from __future__ import annotations

# Standard library
from pathlib import Path
from dataclasses import dataclass

# Third-party
import sep
import numpy as np
from astropy.table import Table

### Inherited from existing example:
# Project
#from . import utils
#from .. import io
#from ..log import logger


sep.set_extract_pixstack(500000)
default_kernel = np.array([[1,2,1], [2,4,2], [1,2,1]])
default_flux_aper = [2.5, 5, 10]
default_flux_ann = [(3, 6), (5, 8)]


__all__ = [
    'extract_sources'
]

def log10(val: float | np.ndarray, fill_val: float = -99.0) -> float | np.ndarray:
    """
    Calculate log10, ignoring values that are less than or equal to zero.
    
    
    Parameters
    ----------
    val : float or np.ndarray
        Value(s) for which take logarithm.
    fill_val : int, optional
        Ignored value replacement, by default -99.

    Returns
    -------
    _ : float or np.array
        Base 10 logarithm of value(s). 
    """
    return np.log10(val, out=fill_val * np.ones_like(val), where=val > 0)


def _byteswap(arr):
    """
    If array is in big-endian byte order (as astropy.io.fits
    always returns), swap to little-endian for SEP.

    Parameters
    ----------
    arr : np.ndarray

    Returns
    -------
    np.ndarray
    """
    if arr is not None and arr.dtype.byteorder=='>':
        arr = arr.byteswap().newbyteorder()
    return arr


@dataclass
class Sources:
    """Data class to hold a source catalog and its associated segmentation map."""
    cat: Table
    segmap: np.ndarray


def extract_sources(
    path_or_pixels: np.ndarray, #Path | str | np.ndarray, 
    thresh: float = 2.5, 
    minarea: int = 5, 
    filter_kernel: np.ndarray = default_kernel, 
    filter_type: str = 'matched', 
    deblend_nthresh: int = 32, 
    deblend_cont: float = 0.005, 
    clean: bool = True, 
    clean_param: float = 1.0,
    bw: int = 64, 
    bh: int = None, 
    fw: int = 3, 
    fh: int = None, 
    mask: np.ndarray = None,
    subtract_sky: bool = True,
    flux_aper: list[float] = default_flux_aper,
    flux_ann: list[tuple[float, float]] = default_flux_ann,
    zpt=None,
    logger=None,
    **kwargs
):
    """
    Extract sources using sep.
    
    https://sep.readthedocs.io

    Parameters
    ----------
    path_or_pixels : pathlib.Path or str or np.ndarray
        Image path or pixels.
    thresh : float, optional
        Threshold pixel value for detection., by default 2.5.
    minarea : int, optional
        Minimum number of pixels required for an object, by default 5.
    filter_kernel : np.ndarray, optional
        Filter kernel used for on-the-fly filtering (used to enhance detection). 
        Default is a 3x3 array: [[1,2,1], [2,4,2], [1,2,1]].
    filter_type : str, optional
        Filter treatment. This affects filtering behavior when a noise array is 
        supplied. 'matched' (default) accounts for pixel-to-pixel noise in the filter 
        kernel. 'conv' is simple convolution of the data array, ignoring pixel-to-pixel 
        noise across the kernel. 'matched' should yield better detection of faint 
        sources in areas of rapidly varying noise (such as found in coadded images 
        made from semi-overlapping exposures). The two options are equivalent 
        when noise is constant. Default is 'matched'.
    deblend_nthresh : int, optional
        Number of thresholds used for object deblending, by default 32.
    deblend_cont : float, optional
        Minimum contrast ratio used for object deblending. Default is 0.005. 
        To entirely disable deblending, set to 1.0.    
    clean : bool, optional
        If True (default), perform cleaning.
    clean_param : float, optional
        Cleaning parameter (see SExtractor manual), by default 1.0.
    bw : int, optional
        Size of background box width in pixels, by default 64.
    bh : int, optional
        Size of background box height in pixels. If None, will use value of `bw`.
    fw : int, optional
        Filter width in pixels, by default 3.
    fh : int, optional
        Filter height in pixels.  If None, will use value of `fw`.
    mask : np.ndarray, optional
        Mask array, by default None.
    subtract_sky : bool, optional
        If True (default), perform sky subtraction. 
    flux_aper : list of float, optional
        Radii of aperture fluxes, by default [2.5, 5, 10].
    flux_ann : list of tuple, optional
        Inner and outer radii for flux annuli, by default [(3, 6), (5, 8)].
    zpt : float, optional
        Photometric zero point. If not None, magnitudes will be calculated.
    **kwargs
        Arguments for sep.Background. 

    Returns
    -------
    source : Sources
        Source object with `cat` and `segmap` as attributes. 
    """
    # Inherited from existing example: more flexible inputs allowable
    #pixels = io.load_pixels(path_or_pixels)
    pixels = path_or_pixels

    # Use square boxes if heights not given.
    bh = bw if bh is None else bh
    fh = fw if fh is None else fh
    
    # Build background map using sep.
    mask = _byteswap(mask)
    data = _byteswap(pixels)
    #bkg = sep.Background(pixels, bw=bw, bh=bh, fw=fw, fh=fh, mask=mask, **kwargs)
    bkg = sep.Background(data, bw=bw, bh=bh, fw=fw, fh=fh, mask=mask, **kwargs)

    # If desired, subtract background. 
    if subtract_sky:
        data = data - bkg

    # Extract sources using sep.
    cat, segmap = sep.extract(
        data, 
        thresh,  
        err=bkg.rms(),
        mask=mask, 
        minarea=minarea, 
        filter_kernel=filter_kernel, 
        filter_type=filter_type,
        deblend_nthresh=deblend_nthresh, 
        deblend_cont=deblend_cont, 
        clean=clean, 
        clean_param=clean_param, 
        segmentation_map=True    
    )
    
    if logger is not None:
        logger.info(f'{len(cat)} sources detected.')

    # Convert catalog to astropy table.
    cat = Table(cat)
    
    # Save segment IDs for future reference.
    cat['seg_id'] = np.arange(1, len(cat) + 1, dtype=int)

    theta = cat['theta']    
    x, y = cat['x'], cat['y']
    a, b = cat['a'], cat['b']

    # Calculate SExtractor's FLUX_AUTO.
    r_kron, _ = sep.kron_radius(data, x, y, a, b, theta, 6.0)
    flux, _, _ = sep.sum_circle(data, x, y, 2.5 * (r_kron), subpix=1)

    r_min = 1.75  
    use_circ = r_kron * np.sqrt(a * b) < r_min
    flux_circ, _, _ = sep.sum_circle(data, x[use_circ], y[use_circ], r_min, subpix=1)
    
    flux[use_circ] = flux_circ
    cat['flux_auto'] = flux
    cat['r_kron'] = r_kron
    
    # HACK: see https://github.com/kbarbary/sep/issues/34.
    cat['fwhm'] = 2 * np.sqrt(np.log(2) * (a**2 + b**2))

    # If zero point given, calculate magnitudes.
    if zpt is not None:
        cat['mag'] = zpt - 2.5 * log10(cat['flux'], fill_val=-99)
        cat['mag_auto'] = zpt - 2.5 * log10(cat['flux_auto'], fill_val=-99)
        
    # Calculate aperture fluxes.
    for r_aper in flux_aper:
        cat[f'f_aper({r_aper})'] = sep.sum_circle(data, x, y, r_aper)[0]
        
    for r_in, r_out in flux_ann:
        cat[f'f_ann({r_in}, {r_out})'] = sep.sum_circann(data, x, y, r_in, r_out)[0]
        
    sources = Sources(
        cat=cat, 
        segmap=segmap, 
    )

    return sources
            