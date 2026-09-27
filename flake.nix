{
  description = "gunsight - scale-invariant GUI locator";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pythonEnv = pkgs.python3.withPackages (ps: with ps; [
          opencv4
          numpy
          click
        ]);
      in
      {
        packages.default = pkgs.writeShellApplication {
          name = "gunsight";
          runtimeInputs = [ pythonEnv ];
          text = ''
            exec ${pythonEnv}/bin/python ${./gunsight.py} "$@"
          '';
        };

        devShells.default = pkgs.mkShell {
          packages = [ pythonEnv pkgs.pyinstaller ];
        };
      }
    );
}
