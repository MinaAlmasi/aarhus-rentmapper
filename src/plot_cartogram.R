
# R script to create cartogram plot of apartment rent in Aarhus based on districts.
# The output is saved to plots/cartogram_plot.jpg.

# by Anton Drasbæk Schiønning (@drasbaek) and Mina Almasi (@MinaAlmasi)
# Spatial Analytics, Cultural Data Science (F2023)

# install pacman 
install.packages("pacman", version="0.5.1", repos="http://cran.rstudio.com/")

# install/load packages
pacman::p_load(tidyverse, sf, cartogram, cowplot)

# load district data
data <- st_read(file.path("results", "district_aggregates.csv"))

# transform to geodata using SF
geodata <- st_as_sf(data, wkt = "geometry")

# ensure rent is numeric
geodata$apartment_rent_sqm_now <- as.numeric(geodata$apartment_rent_sqm_now)

# create cartogram
carto <- cartogram_cont(geodata, "apartment_rent_sqm_now")

# define districts in midtbyen for coloring
midtbyen <- c("Trøjborg", "Universitetet/Kommunehospitalet", "Nordre Kirkegård", "Vestervang/Klostervang/Ø-gaderne", "Ø-gaderne Øst",
              "Østbanetorvet/Nørre Stenbro", "Nørregade", "Latinerkvarteret", "Klostertorv/Vesterbro Torv", "Åboulevarden", "Skolegade/Bispetorv/Europaplads",
              "Mølleparken", "TelefonTorvet", "Fredens Torv", "Ceresbyen/Godsbanen", "Rådhuskvarteret", "De Bynære Havnearealer/Aarhus Ø",
              "Sydhavnen og Marselisborg lystbådehavn", "Frederiksbjerg Vest", "Frederiksbjerg Øst", "Erhvervshavnen", "Botanisk Have/Amtssygehuset")

# set the color palette not midtbyen vs midtbyen
color_palette <- c("#fcacac", rep("#FF595A", length(midtbyen) - 1))

# create columns to identify whether districts are in midtbyen or not
carto$midtbyen <- ifelse(carto$district %in% midtbyen, "yes", "no")
geodata$midtbyen <- ifelse(geodata$district %in% midtbyen, "yes", "no")

# plot the cartogram
plot_cartogram <- ggplot() +
  geom_sf(data = carto, aes(fill = midtbyen, geometry=geometry), color = "white", size = 0.2) +
  scale_fill_manual(values = color_palette) +  # Set the color palette
  ggtitle("[A]") +
  theme_void() + 
  theme(panel.border=element_rect(colour = "black", fill=NA, linewidth=0.5),
        text=element_text(size=17, family = "Times New Roman", face="bold"),
        plot.title=element_text(margin=margin(t=40, b=-23), hjust=0.03),
        plot.margin = margin(1, 1, 25, 1),
        legend.position = "none")

# create non-distorted comparison map
plot_map <- ggplot() +
  geom_sf(data = geodata, aes(fill = midtbyen, geometry=geometry), color = "white", size = 0.2) +
  scale_fill_manual(values = color_palette) +  # Set the color palette
  ggtitle("[B]") +
  theme_void() + 
  theme(panel.border=element_rect(colour = "black", fill=NA, linewidth=0.5),
        text=element_text(size=17, family = "Times New Roman", face="bold"),
        plot.title=element_text(margin=margin(t=40, b=-23), hjust=0.03),
        plot.margin = margin(1, 1, 25, 1),
        legend.position = "none")

# combine the cartogram and normal map using cowplot package
combined_plot <- cowplot::plot_grid(plot_cartogram, plot_map, ncol = 2, labels = c("", ""), hjust = -0.3)

# save plot
ggsave(file.path("plots", "cartogram_plot.jpg"), combined_plot, dpi = 300, width = 10, height = 6)



