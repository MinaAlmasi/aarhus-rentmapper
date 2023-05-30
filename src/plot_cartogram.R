
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
