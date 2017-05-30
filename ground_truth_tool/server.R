library(shiny)
devtools::install_github("SymbolixAU/googleway")
library(googleway)

# heading pitch in view/canvas
# Define server logic required to draw a histogram
shinyServer(function(input, output) {
  setwd("~/Documents/cmsc634_sidewalk-mTurk/")
  # read problem labels data frame
  classes <- c('numeric', 'numeric', 'character', 'character',
               replicate(5, 'factor'), replicate(4, 'numeric'), 'factor')
  names <- c('lng', 'lat', 'label.type', 'label.id', 'asmt.id', 'turker.id',
             'route.id', 'hit.id', 'pano.id', 'canvas.x', 'canvas.y',
             'heading', 'pitch','completed')
  label.data <- read.csv("data/mturk_labels.csv", colClasses = classes,
                         col.names = names)
  # TODO add drag column to data frame
  
  # associate label image names with label type strings
  icon.imgs <- c("Cursor_Other.png", "Cursor_Other.png", "Cursor_Other.png",
                 "Cursor_CurbRamp.png", "Cursor_NoCurbRamp.png",
                 "Cursor_Obstacle.png", "Cursor_SurfaceProblem.png")
  names(icon.imgs) <- c("Other", "NoSidewalk", "Occlusion", "CurbRamp", "NoCurbRamp",
                        "Obstacle", "SurfaceProblem")
  i=1
  
  # render google map
  map.key <- "AIzaSyBoSWFmnDRVTU87KdDJKhTtVU7TuFBpyDc"
  gmap <- google_map(key = map.key,
                     location = c(label.data[i,'lat'],label.data[i,'lng']),
                     zoom=12, search_box = T) %>%
    add_markers(data=label.data, id="label.id", title="label.type", info_window="label.type")#, draggable="drag")
  output$myMap <- renderGoogle_map({
    gmap
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
             tags$img(src="Cursor_Other.png",width="30px",height="30px", # label
                      style=style.str)
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
    })
  })
