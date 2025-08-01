#!/usr/bin/env python3
"""
FileCheck-like tool for end-to-end game testing.

This tool takes a test file with CHECK directives and input commands,
runs the game with those inputs, and verifies the output matches the expected patterns.
"""

import re
import sys
import os
from typing import List, Tuple, Optional, NamedTuple
from dataclasses import dataclass

# Add parent directory to path so we can import game modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.gameloop import run
from src.io_interface import MockIO


class TestMockIO(MockIO):
    """Enhanced MockIO that raises exception when inputs are exhausted."""
    
    def get_input(self, prompt: str) -> str:
        """Return pre-configured input response, raise EOFError when exhausted."""
        self.outputs.append(prompt)  # Store prompt as output too
        if self.input_index < len(self.inputs):
            response = self.inputs[self.input_index]
            self.input_index += 1
            return response
        # Raise EOFError when we run out of inputs instead of returning empty string
        raise EOFError("No more test inputs available")


class CheckDirective(NamedTuple):
    """Represents a CHECK directive from the test file."""
    line_number: int
    directive_type: str  # "CHECK" or "CHECK-NEXT"
    pattern: str
    original_line: str


@dataclass
class TestCase:
    """Represents a parsed test case."""
    inputs: List[str]
    checks: List[CheckDirective]
    filename: str


class FileCheckError(Exception):
    """Exception raised when FileCheck encounters an error."""
    pass


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace for comparison - collapse multiple spaces to single space."""
    return ' '.join(text.split())


def parse_test_file(filename: str) -> TestCase:
    """Parse a test file and extract inputs and CHECK directives."""
    inputs = []
    checks = []
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        raise FileCheckError(f"Test file not found: {filename}")
    
    for line_num, line in enumerate(lines, 1):
        line = line.rstrip()
        
        # Skip empty lines and comments that aren't CHECK directives
        if not line or (line.startswith('#') and not line.startswith('# CHECK')):
            continue
        
        # Parse CHECK directives
        if line.startswith('# CHECK'):
            if line.startswith('# CHECK-NEXT:'):
                pattern = line[13:].strip()
                checks.append(CheckDirective(line_num, "CHECK-NEXT", pattern, line))
            elif line.startswith('# CHECK:'):
                pattern = line[8:].strip()
                checks.append(CheckDirective(line_num, "CHECK", pattern, line))
            else:
                raise FileCheckError(f"Invalid CHECK directive at line {line_num}: {line}")
        
        # Parse input lines (start with '>')
        elif line.startswith('>'):
            input_text = line[1:].strip()
            inputs.append(input_text)
    
    return TestCase(inputs, checks, filename)


def run_game_with_inputs(inputs: List[str]) -> List[str]:
    """Run the game with the given inputs and return all output lines."""
    mock_io = TestMockIO()
    mock_io.set_inputs(inputs)
    
    try:
        # Run the game with mock I/O
        run(mock_io)
    except (EOFError, KeyboardInterrupt):
        # Game exits when it runs out of inputs, that's expected
        pass
    except Exception as e:
        # Capture any other exceptions but continue with output checking
        print(f"Warning: Game execution ended with exception: {e}", file=sys.stderr)
    
    return mock_io.get_all_outputs()


def check_output(outputs: List[str], checks: List[CheckDirective]) -> Tuple[bool, Optional[str]]:
    """
    Check if the output matches the CHECK directives.
    Returns (success, error_message).
    """
    output_index = 0
    check_index = 0
    
    while check_index < len(checks):
        check = checks[check_index]
        
        if check.directive_type == "CHECK":
            # Find the pattern starting from current output position
            found = False
            for i in range(output_index, len(outputs)):
                if normalize_whitespace(check.pattern) in normalize_whitespace(outputs[i]):
                    output_index = i + 1
                    found = True
                    break
            
            if not found:
                return False, f"CHECK at line {check.line_number} failed:\n" \
                             f"  Expected: {check.pattern}\n" \
                             f"  Searched through {len(outputs) - output_index} remaining output lines"
        
        elif check.directive_type == "CHECK-NEXT":
            # Check the very next output line
            if output_index >= len(outputs):
                return False, f"CHECK-NEXT at line {check.line_number} failed:\n" \
                             f"  Expected: {check.pattern}\n" \
                             f"  But no more output lines available"
            
            if normalize_whitespace(check.pattern) not in normalize_whitespace(outputs[output_index]):
                return False, f"CHECK-NEXT at line {check.line_number} failed:\n" \
                             f"  Expected: {check.pattern}\n" \
                             f"  Got: {outputs[output_index]}"
            
            output_index += 1
        
        check_index += 1
    
    return True, None


def run_filecheck(test_filename: str, verbose: bool = False) -> bool:
    """
    Run FileCheck on a test file.
    Returns True if all checks pass, False otherwise.
    """
    try:
        # Parse the test file
        test_case = parse_test_file(test_filename)
        
        if verbose:
            print(f"Running test: {test_filename}")
            print(f"Inputs: {test_case.inputs}")
            print(f"Checks: {len(test_case.checks)} directives")
        
        # Run the game with inputs
        outputs = run_game_with_inputs(test_case.inputs)
        
        if verbose:
            print(f"Game produced {len(outputs)} output lines")
            print("Game output:")
            for i, output in enumerate(outputs):
                print(f"  {i:3}: {output}")
        
        # Check the outputs against CHECK directives
        success, error_msg = check_output(outputs, test_case.checks)
        
        if success:
            if verbose:
                print("PASS: All checks passed!")
            return True
        else:
            print(f"FAIL: Test failed: {test_filename}")
            print(error_msg)
            if verbose:
                print("\nFull game output:")
                for i, output in enumerate(outputs):
                    print(f"  {i:3}: {output}")
            return False
    
    except FileCheckError as e:
        print(f"ERROR: FileCheck error: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        return False


def main():
    """Main entry point for the filecheck tool."""
    if len(sys.argv) < 2:
        print("Usage: python filecheck.py <test_file> [--verbose]")
        print("       python filecheck.py --help")
        sys.exit(1)
    
    if sys.argv[1] == '--help':
        print(__doc__)
        print("\nUsage: python filecheck.py <test_file> [--verbose]")
        print("\nTest file format:")
        print("  # CHECK: <pattern>     - Find pattern anywhere in remaining output")
        print("  # CHECK-NEXT: <pattern> - Find pattern in the very next output line")
        print("  > <input>              - Input to send to the game")
        print("\nExample:")
        print("  # CHECK: What do we do next?:")
        print("  > call phone")
        print("  # CHECK: What number?:")
        print("  > 288-7955")
        sys.exit(0)
    
    test_file = sys.argv[1]
    verbose = '--verbose' in sys.argv
    
    success = run_filecheck(test_file, verbose)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()