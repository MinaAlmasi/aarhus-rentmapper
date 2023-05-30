'''
R script to create cartogram plot of apartment rent in Aarhus based on districts.
The output is saved to plots/cartogram_plot.jpg.

Requires the package "pacman" to be installed. This can be achieved as such from your R console:
  install.packages("pacman")

by Anton Drasbæk Schiønning (@drasbaek) and Mina Almasi (@MinaAlmasi)
Spatial Analytics, Cultural Data Science (F2023)
'''


# install/load packages
pacman::p_load(tidyverse, sf, cartogram)

# load district data
data <- st_read(file.path("..", "data", "district_aggregates.csv"))

# transform to geodata using SF
geodata <- st_as_sf(data, wkt="geometry")

# ensure rent is numeric
geodata$apartment_rent_sqm_now <- as.numeric(geodata$apartment_rent_sqm_now)

# create cartogram
carto <- cartogram_cont(geodata, "apartment_rent_sqm_now")

# plot the cartogram
plot <- ggplot() +
  geom_sf(data = carto$geometry, fill = "#3F8FC5", color = "white", size = 0.5) +
  theme_void()

# save plot
ggsave(file.path("..", "plots", "cartogram_plot.jpg"), plot, dpi = 300)
