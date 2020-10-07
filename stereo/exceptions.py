class CalibrationError(Exception):
    """Ambiguous calibration error class."""

class CalibrationDimentionsNotMatch(CalibrationError):
    """The dimensions of images used for calibration do not match."""
    
class NoCalibrationImages(CalibrationError):
    """No valid calibration images found in the specified path."""

class CalibrationImagesNotMatch(CalibrationError):
    """The number of elements in the sets of images used for calibration
       do not match.
    """

class NotCalibrated(CalibrationError):
    """Action cannot be completed without performed calibration."""