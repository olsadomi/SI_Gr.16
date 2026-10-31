class VehicleController {
  @GetMapping("/vehicle/{carId}/location")
  Object getLocation(java.util.UUID carId) {
    return vehicleService.getVehicleLocation(carId);
  }
}

