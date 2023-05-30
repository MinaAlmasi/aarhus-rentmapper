
# R script to create cartogram plot of apartment rent in Aarhus based on districts.
# The output is saved to plots/cartogram_plot.jpg.

# Requires the package 'pacman' to be installed. This can be achieved as such from your R console:
    # install.packages('pacman')

# by Anton Drasbæk Schiønning (@drasbaek) and Mina Almasi (@MinaAlmasi)
# Spatial Analytics, Cultural Data Science (F2023)


# install/load packages
pacman::p_load(tidyverse, sf, cartogram, cowplot)

# load district data
data <- st_read(file.path("..", "data", "district_aggregates.csv"))

# transform to geodata using SF
geodata <- st_as_sf(data, wkt = "geometry")

# ensure rent is numeric
geodata$apartment_rent_sqm_now <- as.numeric(geodata$apartment_rent_sqm_now)

# create cartogram
carto <- cartogram_cont(geodata, "apartment_rent_sqm_now")

# plot the cartogram
plot_cartogram <- ggplot() +
  geom_sf(data = carto$geometry, fill = "#3F8FC5", color = "white", size = 0.2) +
  ggtitle("[A]") +
  theme_void() + 
  theme(panel.border=element_rect(colour = "black", fill=NA, linewidth=0.5),
        text=element_text(size=17, family = "Times New Roman", face="bold"),
        plot.title=element_text(margin=margin(t=40, b=-23), hjust=0.03),
        plot.margin = margin(1, 1, 25, 1))

# create non-distorted map
plot_map <- ggplot() +
  geom_sf(data = geodata, fill = "#3F8FC5", color = "white", size = 0.2) +
  ggtitle("[B]") +
  theme_void() + 
  theme(panel.border=element_rect(colour = "black", fill=NA, linewidth=0.5),
        text=element_text(size=17, family = "Times New Roman", face="bold"),
        plot.title=element_text(margin=margin(t=40, b=-23), hjust=0.03),
        plot.margin = margin(1, 1, 25, 1))


# Combine the cartogram and map using cowplot package
combined_plot <- cowplot::plot_grid(plot_cartogram, plot_map, ncol = 2, labels = c("", ""), hjust = -0.3)

# Save plot
ggsave(file.path("..", "plots", "cartogram_plot.jpg"), combined_plot, dpi = 300, width=10, height = 6)


