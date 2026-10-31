class VehicleController {
  @GetMapping("/vehicle/{carId}/location")
  Object getLocation(java.util.UUID carId) {
    Request request = currentRequest();
    vehicleService.checkOwnership(carId, request);
    return vehicleService.getVehicleLocation(carId);
  }
}

