namespace py fireflys

struct PhaseResponse {
  1: double phase
}

service FireflyService {
  PhaseResponse getPhase(1: i32 id)
}
