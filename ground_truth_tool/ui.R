library(shiny)
library(googleway)

# Define UI for application that draws a histogram
shinyUI(fluidPage(
  
  # Application title
  titlePanel("Let's resolve some conflicts!"),
  
  sidebarLayout(
    mainPanel(
      uiOutput(outputId="sv"),
      google_mapOutput("myMap"),
      actionButton("test.button","click me")
    ),
    sidebarPanel("This is where words will go")
  )
))
