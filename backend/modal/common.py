from modal import NetworkFileSystem, Stub

stub = Stub("ai-landscape-visualizer")
volume = NetworkFileSystem.persisted("data")
