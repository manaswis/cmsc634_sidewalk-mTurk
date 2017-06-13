library(shiny)
#devtools::install_github("SymbolixAU/googleway")
library(googleway)
library(leaflet)

# heading pitch in view/canvas
# Define server logic required to draw a histogram
shinyServer(function(input, output) {
  setwd("~/Documents/sidewalk-chi2018/")
  # read problem labels data frame
  classes <- c('numeric', 'numeric', 'character', 'character',
               replicate(5, 'factor'), replicate(4, 'numeric'), 'factor',
               'character', 'numeric', 'factor')
  names <- c('lng', 'lat', 'label.type', 'label.id', 'asmt.id', 'turker.id',
             'route.id', 'hit.id', 'pano.id', 'canvas.x', 'canvas.y',
             'heading', 'pitch', 'completed', 'coords', 'id', 'cluster')
  label.data <- read.csv("data/ground_truth-problem_labels-clustered.csv",
                         colClasses = classes, col.names = names)
  
  # associate label image names with label type strings
  icon.imgs <- c("Cursor_Other.png", "Cursor_Other.png", "Cursor_Other.png",
                 "Cursor_CurbRamp.png", "Cursor_NoCurbRamp.png",
                 "Cursor_Obstacle.png", "Cursor_SurfaceProblem.png")
  names(icon.imgs) <- c("Other", "NoSidewalk", "Occlusion", "CurbRamp", "NoCurbRamp",
                        "Obstacle", "SurfaceProblem")
  label.data$icons <- unname(icon.imgs[label.data$label.type])
  
  label.data$drag <- TRUE
  i=1
  label.subset <- label.data[label.data$cluster == label.data[i,'cluster'],]
  leaflet.icons <- icons(label.subset$icons)
  
  # render leaflet map
  map.key <- "AIzaSyBoSWFmnDRVTU87KdDJKhTtVU7TuFBpyDc"
  output$myMap <- renderLeaflet({
    leaflet(options = leafletOptions(maxZoom = 19)) %>%
      addProviderTiles(providers$Thunderforest.Transport) %>%
      addMarkers(data = label.subset, lng = ~lng, lat = ~lat,
                 icon = leaflet.icons, label = ~label.id)
  })
  
  # render static google street view image w/ a label on it
  sv <- google_streetview(panorama_id = as.character(label.data[i,'pano.id']),
                          key = map.key, response_check = TRUE,
                          size = c(720,480), output="html",
                          heading=label.data[i,'heading'], pitch=label.data[i,'pitch'])
  style.str <- paste0("position:absolute;left:", label.data[i,'canvas.x'],
                      "px;top:", label.data[i,'canvas.y'], "px;")
  output$sv <- renderUI({
    tags$img(src=sv, width="720", height="480px", # actual SV image
             style="position:relative;left:0px;top:0px;",
             tags$img(src=icon.imgs[label.data[i,"label.type"]], width="30px",
                      height="30px", style=style.str)
             )
    })
  
  # TODO when label in map is clicked, load that label on the right SV, right
  #      now there is a partial implementation where a new test SV and label
  #      are brought up when a button is clicked
  observeEvent(input$test.button, {
    i <<- i + 1
    # get new GSV image
    sv <- google_streetview(panorama_id = as.character(label.data[i,'pano.id']),
                            key = map.key, response_check = TRUE,
                            size = c(720,480), output="html",
                            heading=label.data[i,'heading'],
                            pitch=label.data[i,'pitch'])
    # render new GSV image with a label on top
    style.str <- paste0("position:absolute;left:", label.data[i,'canvas.x'],
                        "px;top:", label.data[i,'canvas.y'], "px;")
    output$sv <- renderUI({
      tags$img(src=sv,width="720",height="480px",
               style="position:relative;left:0px;top:0px;",
               tags$img(src=icon.imgs[label.data[i,"label.type"]], width="30px",
                        height="30px", style=style.str)
               )
      })
    
    # update map to show current cluster, if cluster has changed
    # TODO find a way to somehow highlight the current label being looked at
    if (label.data[i,'cluster'] != label.data[i-1,'cluster']) {
      output$myMap <- renderLeaflet({
        label.subset <- label.data[label.data$cluster == label.data[i,'cluster'],]
        leaflet.icons <- icons(label.subset$icons)
        leaflet() %>%
          addProviderTiles(providers$Thunderforest.Transport) %>%
          setView(lng = (min(label.subset$lng) + max(label.subset$lng)) / 2,
                  lat = (min(label.subset$lat) + max(label.subset$lat)) / 2,
                  zoom = 19) %>%
          addMarkers(data = label.subset, lng = ~lng, lat = ~lat,
                     icon = leaflet.icons, label = ~label.id)
      })
    }
    })
  })
