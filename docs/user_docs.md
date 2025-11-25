# Oculus - User Documentation

**Oculus** is an easy-to-use web-based tool for searching, processing, and visualizing Sentinel-1 and Sentinel-2 
(and possibly more platforms) satellite data. The platform lets end users select areas and time ranges, apply
mission-specific filters, and quickly view processed imagery in a web browser without knowledge of APIs or GIS tools.

####  The application is running at **[https://oculus.cesnet.cz/](https://oculus.cesnet.cz/)**. No authentication is required.

---

## 3‑Step Quick Guide 

### Step 1: Select Dataset, Area, and Time Range
![Step1](img/user_step_1.png)

* Set the time window (optional) in the **Time from** and **Time to** fields. If not set, the last 7 days will be used.
* Enter the area of interest in the **search box** or input the coordinates as a bbox in the **North-west** and **South-east 
corner** fields. Otherwise, the currently viewed area will be used.
* Select **Datasets** from the respective panel.
* Specify **Additional filters** (optional) such as cloud coverage, polarization, or orbit direction.
* Click on the **Fetch features** button to start searching for products.


### Step 2: Select Product
![Step2](img/user_step_2.png)

* Each product's area is highlighted in the map when hovered over its information card.
* You can copy the link to the product's information by clicking the **files icon** next to the Visualize button.
* Select the product which you want to visualize by clicking the **Visualize button**.


### Step 3: Visualize
![Step3](img/user_step_3.png)

* The product will be displayed on the map. Note that the processing may take a few moments.
* You can use the **Opacity slider** to adjust the opacity of the product over the base map.
* The **Processed products** dropdown list shows all the files that have been processed. You can select a different 
file to view.
* You can download the processed image by clicking the **Download** button.

---

#### For more detailed information about the application, please refer to the [Current State Documentation](./docs.md).
#### In case of any questions, please contact the developers at [collgs@cesnet.cz](mailto:collgs@cesnet.cz).