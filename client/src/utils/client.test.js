import { joinPks } from "./client";

describe("joinPks", () => {
	it("joins integer pks with commas", () => {
		expect(joinPks([1, 2, 3])).toBe("1,2,3");
	});

	it("encodes commas and percent signs in string pks", () => {
		expect(joinPks(["a,b", "50%", "c d"])).toBe("a%2Cb,50%25,c%20d");
	});

	it("returns an empty string for no pks", () => {
		expect(joinPks([])).toBe("");
	});
});
