import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

class VehicleController {

  private VehicleService vehicleService;

  @GetMapping("/vehicle/{carId}/location")
  public Object getLocation(@PathVariable("carId") java.util.UUID carId) {
    return vehicleService.getVehicleLocation(carId);
  }
}