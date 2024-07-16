from modal import NetworkFileSystem, Stub

stub = Stub("mlmap")
volume = NetworkFileSystem.persisted("data")
