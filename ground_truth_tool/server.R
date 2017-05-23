library(shiny)
library(googleway)

# heading pitch in view/canvas
# Define server logic required to draw a histogram
shinyServer(function(input, output) {
  setwd("~/Dropbox/shiny/testApp1/")
  # TODO read problem labels data frame
  # TODO add drag column to data frame
  lables <- data.frame(lat = c(38.9235191345, 38.9235458374),
                       lon = c(-77.0019836426, -77.0019760132),
                       type = c("Obstacle","NoCurbRamp"),
                       drag = c(TRUE, TRUE))
  df <- data.frame(lat = 38.9229545593,
                   lon = -77.0034484863,
                   info = "label 1")
  
  # render google map
  map_key <- "AIzaSyBoSWFmnDRVTU87KdDJKhTtVU7TuFBpyDc"
  gmap <- google_map(location = c(df$lat, df$lon), key = map_key, search_box = T) %>%
    add_markers(data=lables, title="type", info_window="type", draggable="drag")
  output$myMap <- renderGoogle_map({
    gmap
  })
  
  # render static google street view image w/ a label on it
  sv <- google_streetview(panorama_id = "o17ruazNwFEAQ2CA5PuYug",
                          key = map_key, response_check = TRUE,
                          size = c(720,480), output="html",
                          heading=218.8125, pitch=-22.75)
  output$sv <- renderUI({
    tags$img(src=sv, width="720", height="480px", # actual SV image
             style="position:relative;left:0px;top:0px;",
             tags$img(src="Cursor_Other.png",width="30px",height="30px", # label
                      style="position:absolute;left:344px;top:162px;")
             )
    })
  
  # TODO when label in map is clicked, load that label on the right SV, right
  #      now there is a partial implementation where a new test SV and label
  #      are brought up when a button is clicked
  observeEvent(input$test.button, {
    # get new GSV image
    sv <- google_streetview(panorama_id = "kti20on3Kpa13rmnGnMueA",
                            key = map_key, response_check = TRUE,
                            size = c(720,480), output="html",
                            heading=354.75, pitch=-30.125)
    # render new GSV image with a label on top
    output$sv <- renderUI({
      tags$img(src=sv,width="720",height="480px",
               style="position:relative;left:0px;top:0px;",
               tags$img(src="Cursor_CurbRamp.png",width="30px",height="30px",
                        style="position:absolute;left:377px;top:254px;")
               )
      })
    })
  })
