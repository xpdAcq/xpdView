==================
xpdview Change Log
==================

.. current developments

v0.5.1
====================

**Fixed:**

* Have a safe default for start doc dimensions in case there are none
* Handle null dimensions more gracefully



v0.5.0
====================

**Changed:**

* A single ``Waterfall`` instance can be used for all 1D data in a stream
* ``LiveWaterfall`` will inspect the events for which 1D data to plot



v0.4.1
====================

**Fixed:**

* Use ``bluesky`` for callback base to avoid circular deps



v0.4.0
====================

**Changed:**

* Waterfall plot is now more efficent
* The waterfall callback now supports data which it can't handle, it just
  ignores the data. This allows us to support the RunRouter.



v0.3.2
====================

**Changed:**

* Limit the number of 1D plots visualized so plotting doesn't take forever




v0.3.1
====================

**Added:**

* Rever for releases

* Conda config for travis




