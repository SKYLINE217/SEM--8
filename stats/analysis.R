# Inferential Statistics Requirement: R script for control charts and regression

# Check if packages are installed, if not, we can't do much in a script without internet, 
# but we assume the environment has them or we use base R where possible.
# install.packages("qcc", repos="http://cran.us.r-project.org")

# Load Data
data <- read.csv("../sensor_data.csv")

# Create output file
sink("statistical_report.txt")

cat("=== IoT-Enabled Compression Molding Statistical Report ===\n\n")

# 1. Linear Regression
# Inferential Statistics Requirement: Linear regression: density ~ platen_temp_upper + hydraulic_pressure
cat("--- Linear Regression Analysis ---\n")
if("density" %in% colnames(data)) {
  model <- lm(density ~ platen_temp_upper + hydraulic_pressure, data=data)
  print(summary(model))
} else {
  cat("Density data not available for regression.\n")
}

# 2. Hypothesis Test
# Inferential Statistics Requirement: Compare pressure variance pre/post simulated maintenance (F-test)
cat("\n--- Hypothesis Test (Pressure Variance) ---\n")
# Simulating split of data for pre/post maintenance (first half vs second half)
n <- nrow(data)
if(n > 10) {
  pre_maint <- data$hydraulic_pressure[1:(n/2)]
  post_maint <- data$hydraulic_pressure[((n/2)+1):n]
  
  f_test <- var.test(pre_maint, post_maint)
  print(f_test)
} else {
  cat("Insufficient data for F-test.\n")
}

# 3. Process Capability (Simplified calculation if qcc not available)
cat("\n--- Process Capability Indices ---\n")
target_temp <- 165
lsl <- 162
usl <- 168
mean_temp <- mean(data$platen_temp_upper, na.rm=TRUE)
sd_temp <- sd(data$platen_temp_upper, na.rm=TRUE)

Cp <- (usl - lsl) / (6 * sd_temp)
Cpk <- min((usl - mean_temp) / (3 * sd_temp), (mean_temp - lsl) / (3 * sd_temp))

cat(paste("Cp:", round(Cp, 4), "\n"))
cat(paste("Cpk:", round(Cpk, 4), "\n"))

sink()

# 4. Control Charts
# Inferential Statistics Requirement: Generate control charts (X-bar/R)
pdf("control_charts.pdf")
if(require("qcc")) {
  qcc(data$platen_temp_upper, type="xbar.one", title="Temperature Control Chart")
} else {
  plot(data$platen_temp_upper, type="o", main="Temperature Control Chart (Base R)", ylab="Temp")
  abline(h=mean_temp, col="blue")
  abline(h=mean_temp + 3*sd_temp, col="red", lty=2)
  abline(h=mean_temp - 3*sd_temp, col="red", lty=2)
}
dev.off()

cat("Statistical analysis completed. Report saved to statistical_report.txt and control_charts.pdf.\n")
