library(shiny)
library(googleway)

# Define UI for application that draws a histogram
shinyUI(fluidPage(
  
  titlePanel("Let's resolve some conflicts!"),
  
  fluidRow(
    column(6, leafletOutput("myMap")),
    column(6, uiOutput(outputId="sv"))),
  hr(),
  actionButton("test.button","click me")
))
